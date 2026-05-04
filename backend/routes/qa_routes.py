"""
Q&A routes for historical questions
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import asyncio

qa_bp = Blueprint('qa', __name__)

# Global state (will be set by main app)
vector_index = None
text_map = None
smithsonian_api_key = None

def set_vector_db(index, t_map):
    """Set vector database for this blueprint"""
    global vector_index, text_map
    vector_index = index
    text_map = t_map

def set_museum_api_key(key):
    """Set museum API key"""
    global smithsonian_api_key
    smithsonian_api_key = key

async def get_ai_response(question):
    """
    Get comprehensive AI response for historical question
    
    Args:
        question: User's question string
        
    Returns:
        dict: Response with answer, source, and metadata
    """
    # Import only when function is called
    from utils.history_utils import is_historical_question, generate_history_prompt, generate_fallback_response
    from utils.vector_utils import search_vector_db
    from utils.wikipedia_utils import search_and_summarize, get_related_articles, get_wikipedia_summary
    from utils.museum_utils import search_multiple_museums
    from utils.ai_utils import is_gemini_configured, generate_content

    def word_count(text):
        return len(text.split()) if text else 0
    
    # Check if question is historical
    if not is_historical_question(question):
        return {
            'response': "I specialize in world history and historical topics. Please ask about historical events, figures, civilizations, wars, cultural movements, or historical places from any time period and region.",
            'source': 'filter',
            'wikipedia_info': None,
            'museum_data': None
        }
    
    # Run independent lookups in parallel so the request does not wait
    # on each network call one after another.
    lookup_tasks = []
    has_vector_db = bool(vector_index and text_map)

    if has_vector_db:
        lookup_tasks.append(asyncio.to_thread(search_vector_db, question, vector_index, text_map, 2))
    lookup_tasks.append(asyncio.to_thread(search_and_summarize, question))
    lookup_tasks.append(asyncio.to_thread(
        search_multiple_museums,
        question,
        api_key=smithsonian_api_key,
        limit_per_source=2
    ))

    lookup_results = await asyncio.gather(*lookup_tasks, return_exceptions=True)

    result_offset = 0
    relevant_context = None
    if has_vector_db:
        vector_result = lookup_results[0]
        result_offset = 1
        if not isinstance(vector_result, Exception) and vector_result:
            relevant_context = "\n\n".join(vector_result)

    wikipedia_result = lookup_results[result_offset]
    museum_result = lookup_results[result_offset + 1]

    wikipedia_info = wikipedia_result if not isinstance(wikipedia_result, Exception) else None

    # Get museum artifacts (optional, don't block on failure)
    museum_data = None
    if not isinstance(museum_result, Exception) and museum_result and museum_result.get('total_count', 0) > 0:
        museum_data = museum_result
    elif isinstance(museum_result, Exception):
        print(f"Museum search failed: {str(museum_result)}")
    
    # Try AI response if configured
    if is_gemini_configured():
        try:
            prompt = generate_history_prompt(
                question,
                relevant_context,
                wikipedia_info,
                museum_data
            )
            
            ai_response = await asyncio.to_thread(
                generate_content,
                prompt,
                0.7,
                3072
            )

            # If the response is too short, ask for an expanded long-form answer.
            if ai_response and word_count(ai_response) < 700:
                expand_prompt = (
                    f"Expand and deepen this answer to approximately 900-1100 words. "
                    f"Keep markdown headings and improve detail, chronology, and analysis.\n\n"
                    f"Original question: {question}\n\n"
                    f"Current answer:\n{ai_response}"
                )
                expanded_response = await asyncio.to_thread(
                    generate_content,
                    expand_prompt,
                    0.6,
                    3072
                )
                if expanded_response and word_count(expanded_response) > word_count(ai_response):
                    ai_response = expanded_response

            # Retry once with a shorter prompt to handle occasional model
            # refusals/timeouts on long context payloads.
            if not ai_response and wikipedia_info:
                short_prompt = (
                    f"Provide a detailed markdown answer about: {question}. "
                    "Target around 900-1100 words and include sections: Overview, Historical Context, "
                    "Key Facts, Cultural Impact, Interesting Details, Modern Legacy, Related Topics. "
                    f"Reference this context: {wikipedia_info.get('extract', '')}"
                )
                ai_response = await asyncio.to_thread(
                    generate_content,
                    short_prompt,
                    0.5,
                    2048
                )
            
            if ai_response:
                return {
                    'response': ai_response,
                    'source': 'ai',
                    'wikipedia_info': wikipedia_info,
                    'museum_data': museum_data,
                    'context_used': relevant_context is not None
                }
        except Exception as e:
            print(f" AI response error: {str(e)}")
    
    # Fallback to Wikipedia-based response
    related_summaries = []
    if wikipedia_info:
        try:
            seed_title = wikipedia_info.get('title') or question
            related_titles = await asyncio.to_thread(get_related_articles, seed_title, 5)
            for title in related_titles[:5]:
                summary = await asyncio.to_thread(get_wikipedia_summary, title)
                if summary and summary.get('extract'):
                    related_summaries.append({
                        'title': summary.get('title', title),
                        'extract': summary.get('extract', '')
                    })
        except Exception as related_error:
            print(f"Related summary fallback warning: {str(related_error)}")

    fallback = generate_fallback_response(
        question,
        relevant_context,
        wikipedia_info,
        related_summaries=related_summaries
    )
    return {
        'response': fallback,
        'source': 'fallback',
        'wikipedia_info': wikipedia_info,
        'museum_data': museum_data,
        'context_used': relevant_context is not None
    }

@qa_bp.route('/ask', methods=['POST'])
def ask_question():
    """
    Main question answering endpoint
    
    Expected JSON:
        {
            "question": "What was the significance of the Roman Empire?"
        }
        
    Returns:
        {
            "question": "...",
            "answer": "...",
            "source": "ai|fallback|filter",
            "wikipedia_info": {...},
            "museum_data": {...},
            "timestamp": "..."
        }
    """
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        # Get AI response
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(get_ai_response(question))
        finally:
            loop.close()
        
        response = {
            'question': question,
            'answer': result['response'],
            'source': result['source'],
            'wikipedia_info': result.get('wikipedia_info'),
            'museum_data': result.get('museum_data'),
            'context_used': result.get('context_used', False),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Question processing error: {str(e)}")
        return jsonify({'error': f'Failed to process question: {str(e)}'}), 500

@qa_bp.route('/quick-facts/<topic>', methods=['GET'])
def quick_facts(topic):
    """
    Get quick facts about a historical topic
    
    Args:
        topic: Historical topic name (URL parameter)
        
    Returns:
        Quick summary and key facts
    """
    try:
        from utils.wikipedia_utils import search_and_summarize

        # Get Wikipedia summary
        wikipedia_info = search_and_summarize(topic)
        
        if not wikipedia_info:
            return jsonify({'error': f'No information found for topic: {topic}'}), 404
        
        return jsonify({
            'topic': topic,
            'summary': wikipedia_info.get('extract', ''),
            'description': wikipedia_info.get('description', ''),
            'thumbnail': wikipedia_info.get('thumbnail', ''),
            'url': wikipedia_info.get('url', ''),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve facts: {str(e)}'}), 500

@qa_bp.route('/related/<topic>', methods=['GET'])
def related_topics(topic):
    """
    Get related historical topics
    
    Args:
        topic: Historical topic name (URL parameter)
        
    Returns:
        List of related topics with summaries
    """
    try:
        from utils.wikipedia_utils import get_related_articles
        
        related = get_related_articles(topic, limit=5)
        
        return jsonify({
            'topic': topic,
            'related_topics': related,
            'count': len(related),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve related topics: {str(e)}'}), 500
