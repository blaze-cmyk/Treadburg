/**
 * This script helps debug OAuth issues
 * Add this to your browser console when testing OAuth flows
 */

// Patches the fetch API to log OAuth-related requests
(function() {
  const originalFetch = window.fetch;
  
  window.fetch = function(...args) {
    const url = args[0];
    const options = args[1] || {};
    
    // Only log requests to Supabase auth endpoints
    if (typeof url === 'string' && url.includes('/auth/v1/')) {
      console.group('OAuth Debug - Fetch Request');
      console.log('URL:', url);
      console.log('Method:', options.method || 'GET');
      console.log('Headers:', options.headers);
      
      if (options.body) {
        try {
          console.log('Body:', JSON.parse(options.body));
        } catch (e) {
          console.log('Body:', options.body);
        }
      }
      console.groupEnd();
    }
    
    return originalFetch.apply(this, args)
      .then(response => {
        if (typeof url === 'string' && url.includes('/auth/v1/')) {
          console.group('OAuth Debug - Fetch Response');
          console.log('URL:', url);
          console.log('Status:', response.status);
          console.log('Status Text:', response.statusText);
          console.groupEnd();
        }
        return response;
      })
      .catch(error => {
        if (typeof url === 'string' && url.includes('/auth/v1/')) {
          console.group('OAuth Debug - Fetch Error');
          console.log('URL:', url);
          console.error('Error:', error);
          console.groupEnd();
        }
        throw error;
      });
  };
  
  // Monitor location changes
  let lastHref = window.location.href;
  setInterval(() => {
    if (window.location.href !== lastHref) {
      console.group('OAuth Debug - URL Change');
      console.log('From:', lastHref);
      console.log('To:', window.location.href);
      
      // Parse URL for auth parameters
      const url = new URL(window.location.href);
      const authParams = {};
      url.searchParams.forEach((value, key) => {
        if (key.includes('auth') || key === 'error' || key === 'code' || key === 'token') {
          authParams[key] = value;
        }
      });
      
      if (Object.keys(authParams).length > 0) {
        console.log('Auth Parameters:', authParams);
      }
      
      console.groupEnd();
      lastHref = window.location.href;
    }
  }, 100);
  
  console.log('OAuth Debug Tools Activated - Monitoring for auth requests and redirects');
})();
