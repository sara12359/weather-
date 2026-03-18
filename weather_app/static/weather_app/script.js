const WEATHER_IMAGES = {
    'Clear': 'https://images.unsplash.com/photo-1601297183305-6df142704ea2?auto=format&fit=crop&w=1920&q=80',
    'Clouds': 'https://images.unsplash.com/photo-1534088568595-a066f7105a21?auto=format&fit=crop&w=1920&q=80',
    'Rain': 'https://images.unsplash.com/photo-1534274988757-a28bf1a57c17?auto=format&fit=crop&w=1920&q=80',
    'Thunderstorm': 'https://images.unsplash.com/photo-1605727285676-3f8865141930?auto=format&fit=crop&w=1920&q=80',
    'Snow': 'https://images.unsplash.com/photo-1491002052546-bf38f186af56?auto=format&fit=crop&w=1920&q=80',
    'Mist': 'https://images.unsplash.com/photo-1485236715568-15bccd4e8cda?auto=format&fit=crop&w=1920&q=80',
    'Default': 'https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?auto=format&fit=crop&w=1920&q=80'
};

function updateBackground(condition) {
    const overlay = document.querySelector('.bg-overlay');
    if (!overlay) return;

    const imageUrl = WEATHER_IMAGES[condition] || WEATHER_IMAGES['Default'];
    const tempImg = new Image();
    tempImg.src = imageUrl;
    tempImg.onload = () => {
        overlay.style.backgroundImage = `url('${imageUrl}')`;
        overlay.style.opacity = '1';
    };
}

document.addEventListener('DOMContentLoaded', () => {
    // Background handling
    const weatherCondition = document.body.dataset.condition;
    if (weatherCondition) {
        updateBackground(weatherCondition);
    } else {
        updateBackground('Default');
    }

    // Loader logic
    const forms = document.querySelectorAll('form:not(.no-loader)');
    const loader = document.getElementById('loader');
    forms.forEach(form => {
        form.addEventListener('submit', () => {
            if (loader) loader.classList.add('active');
        });
    });

    // Geolocation logic (only on home if no data)
    const isHome = document.body.dataset.page === 'home';
    const hasData = document.body.dataset.hasData === 'true';
    
    if (isHome && !hasData && "geolocation" in navigator) {
        const loader = document.getElementById('loader');
        if (loader) loader.classList.add('active');

        navigator.geolocation.getCurrentPosition(position => {
            const form = document.createElement('form');
            form.method = 'POST';
            form.innerHTML = `
                <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                <input type="hidden" name="lat" value="${position.coords.latitude}">
                <input type="hidden" name="lon" value="${position.coords.longitude}">
            `;
            document.body.appendChild(form);
            form.submit();
        }, () => {
            if (loader) loader.classList.remove('active');
        }, { timeout: 5000 });
    }
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
