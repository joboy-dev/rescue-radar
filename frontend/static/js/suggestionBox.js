const locationInput = document.getElementById('location');
const suggestionBox = document.getElementById('suggestion-box');

const baseUrl = "{{ request.base_url }}"

locationInput.addEventListener('input', async () => {
    const query = locationInput.value.trim();

    if (query.length < 2) { // Trigger only after 2 characters
        suggestionBox.style.display = 'none';
        return;
    }

    let queryList = query.split(',');
    let city = '';
    let state = '';
    if (queryList.length > 1) {
        city = queryList[-2]
        state = queryList[-1]
    } else {
        city = query;
        state = '';
    }

    try {
        // Fetch location data from the API
        const response = await fetch(`${baseUrl}locations/search?city=${city}&state=${state}`);
        if (!response.ok) throw new Error('Failed to fetch location data.');

        const suggestions = await response.json();

        // Populate the suggestion box
        if (suggestions.length > 0) {
            suggestionBox.innerHTML = suggestions.map(suggestion => `
                <div class="suggestion-item" data-value="${suggestion.city}, ${suggestion.state}">
                    ${suggestion.city}, ${suggestion.state}
                </div>
            `).join('');
            suggestionBox.style.display = 'block';
        } else {
            suggestionBox.style.display = 'none';
        }
    } catch (error) {
        console.error('Error fetching suggestions:', error);
    }
});

// Handle suggestion selection
suggestionBox.addEventListener('click', (e) => {
    if (e.target.classList.contains('suggestion-item')) {
        locationInput.value = e.target.getAttribute('data-value');
        suggestionBox.style.display = 'none';
    }
});

// Hide suggestions when clicking outside
document.addEventListener('click', (e) => {
    if (!suggestionBox.contains(e.target) && e.target !== locationInput) {
        suggestionBox.style.display = 'none';
    }
});