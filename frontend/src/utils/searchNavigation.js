export const SEARCH_ROUTE = '/search';

const normalizeQuery = (value) => (value || '').replace(/\s+/g, ' ').trim();

export const createSearchState = (query, source = '') => ({
  query: normalizeQuery(query),
  autoSearch: true,
  source,
});

export const navigateToSearch = (navigate, query, source = '') => {
  const normalized = normalizeQuery(query);
  if (!normalized) {
    return false;
  }

  navigate(SEARCH_ROUTE, { state: createSearchState(normalized, source) });
  return true;
};