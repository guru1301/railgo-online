import re

def main():
    file_path = 'static/trains.html'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add CSS
    new_css = """
    /* Date Slider & New UI Styles */
    .class-card {
        min-width: 140px;
        background-color: rgba(255, 255, 255, 0.7);
        cursor: pointer;
        transition: all 0.2s;
        border: 1px solid #ccc;
    }
    .dark-mode .class-card {
        background-color: rgba(0, 0, 0, 0.3);
        border-color: #555;
    }
    .class-card:hover {
        border-color: #FF69B4;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(255, 105, 180, 0.2);
    }
    .class-card.available {
        background-color: rgba(40, 167, 69, 0.1);
        border-color: rgba(40, 167, 69, 0.5);
    }
    .class-card.unavailable {
        background-color: rgba(220, 53, 69, 0.1);
        border-color: rgba(220, 53, 69, 0.3);
    }
    .banner-fcf {
        background: linear-gradient(90deg, #0f9b0f, #28a745, #34ce57);
        border-radius: 8px;
    }
    .date-slider-container {
        display: flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 8px;
        border-bottom: 1px solid #eee;
        padding: 0 10px;
    }
    .dark-mode .date-slider-container {
        background: rgba(0, 0, 0, 0.5);
        border-bottom: 1px solid #333;
    }
    .date-slider {
        display: flex;
        overflow-x: auto;
        flex-grow: 1;
        scrollbar-width: none;
    }
    .date-slider::-webkit-scrollbar {
        display: none;
    }
    .date-item {
        min-width: 100px;
        text-align: center;
        padding: 10px 5px;
        cursor: pointer;
        border-bottom: 3px solid transparent;
        color: #555;
    }
    .dark-mode .date-item {
        color: #aaa;
    }
    .date-item:hover {
        background-color: rgba(0,0,0,0.05);
    }
    .date-item.active {
        border-bottom: 3px solid #28a745;
        color: #28a745;
        font-weight: bold;
    }
    .dark-mode .date-item.active {
        color: #34ce57;
        border-bottom: 3px solid #34ce57;
    }
    .train-main-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .dark-mode .train-main-card {
        background: rgba(0, 0, 0, 0.6);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .train-card-title {
        font-size: 1.2rem;
        font-weight: bold;
    }
    .class-cards-container {
        padding-bottom: 10px;
    }
    .class-cards-container::-webkit-scrollbar {
        height: 6px;
    }
    .class-cards-container::-webkit-scrollbar-thumb {
        background-color: #ccc;
        border-radius: 10px;
    }
    .availability-text {
        font-size: 0.85rem;
    }
  </style>
"""
    content = content.replace("</style>", new_css)

    # 2. Replace Search Details HTML
    old_search_details = """<div class="search-details mb-4">
<div class="row">
<div class="col-md-8">
<h2 id="route-title">Trains from <span id="source-station">Source</span> to <span id="destination-station">Destination</span></h2>
<p class="mb-0">Journey Date: <span id="journey-date">Date</span> | Class: <span id="class-type-display">Any</span></p>
</div>
<div class="col-md-4 text-md-end mt-3 mt-md-0">
<button class="btn btn-outline-primary modify-search-button" onclick="window.location.href='index.html'">
<i class="bi bi-arrow-left"></i> Modify Search
              </button>
</div>
</div>
</div>"""

    new_search_details = """
<div class="search-details mb-4 p-0 bg-transparent shadow-none" style="border:none;">
    <!-- Route Info -->
    <div class="d-flex justify-content-between align-items-center mb-3">
        <div>
            <h2 id="route-title" class="mb-1 theme-text"><span id="source-name-title">Source</span> to <span id="destination-name-title">Destination</span> Trains</h2>
            <p class="mb-0 text-muted"><span id="train-count">0</span> Trains found between <span id="source-station">Source</span> to <span id="destination-station">Destination</span></p>
        </div>
        <div>
            <button class="btn btn-outline-primary modify-search-button" onclick="window.location.href='index.html'">
                <i class="bi bi-arrow-left"></i> Modify Search
            </button>
        </div>
    </div>

    <!-- Date Slider & Filters -->
    <div class="bg-white rounded shadow-sm mb-3">
        <div class="date-slider-container">
            <div class="fw-bold me-3 text-muted text-center" style="writing-mode: vertical-rl; transform: rotate(180deg); font-size: 0.8rem;" id="slider-month">Apr</div>
            <div class="date-slider" id="date-slider">
                <!-- Dynamically populated dates -->
            </div>
            <div class="ms-3 p-2 text-muted border-start cursor-pointer"><i class="bi bi-calendar3"></i></div>
        </div>
        <div class="d-flex align-items-center p-3 border-top" style="background: rgba(255,255,255,0.02);">
            <strong class="me-4 theme-text">Quick Filters</strong>
            <div class="form-check form-switch me-4">
                <input class="form-check-input" type="checkbox" id="bestAvailable">
                <label class="form-check-label theme-text" for="bestAvailable">Best Available</label>
            </div>
            <div class="form-check form-switch me-4">
                <input class="form-check-input" type="checkbox" id="tatkalOnly">
                <label class="form-check-label theme-text" for="tatkalOnly">Tatkal Only</label>
            </div>
            <div class="form-check form-switch">
                <input class="form-check-input" type="checkbox" id="acOnly">
                <label class="form-check-label theme-text" for="acOnly">AC Only</label>
            </div>
        </div>
    </div>

    <!-- Banner -->
    <div class="banner-fcf d-flex align-items-center justify-content-between p-3 rounded shadow-sm">
        <div class="d-flex align-items-center">
            <i class="bi bi-shield-check fs-1 me-3 text-white opacity-75" style="border: 1px solid white; border-radius: 5px; padding: 5px;"></i>
            <div>
                <h4 class="text-white mb-0 fw-bold">Free Cancellation</h4>
                <div class="text-white">Get full refund of your train fare on cancellation *</div>
            </div>
        </div>
        <div class="text-end">
            <div class="bg-warning text-success fw-bold px-3 py-2 rounded fs-5" style="display:inline-block;">FCF</div>
            <small class="text-white d-block mt-1">*T&C</small>
        </div>
    </div>
</div>
"""
    content = content.replace(old_search_details, new_search_details)

    # 3. Replace JS functions
    # Instead of regex matching, let's locate the <script> and replace everything inside it up to <script src="common.js">
    script_start = content.find("<script>\n    // Get URL Parameters")
    if script_start == -1:
        script_start = content.find("<script>\r\n    // Get URL Parameters")
    
    script_end = content.find("</script>\n<script src=\"common.js\">")
    if script_end == -1:
        script_end = content.find("</script>\r\n<script src=\"common.js\">")
        
    if script_start != -1 and script_end != -1:
        new_script = """<script>
    // Get URL Parameters
    function getUrlParams() {
      const queryString = window.location.search;
      const urlParams = new URLSearchParams(queryString);
      return {
        source: urlParams.get('source'),
        destination: urlParams.get('destination'),
        classType: urlParams.get('classType'),
        date: urlParams.get('date') || new Date().toISOString().split('T')[0]
      };
    }

    function changeDate(newDate) {
        const params = new URLSearchParams(window.location.search);
        params.set('date', newDate);
        window.location.search = params.toString();
    }

    function generateDateSlider(selectedDateStr) {
        const slider = document.getElementById('date-slider');
        const monthLabel = document.getElementById('slider-month');
        slider.innerHTML = '';
        
        const selectedDate = new Date(selectedDateStr);
        const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
        
        monthLabel.textContent = monthNames[selectedDate.getMonth()];
        
        // Generate 3 days before and 3 days after
        for (let i = -3; i <= 3; i++) {
            const d = new Date(selectedDate);
            d.setDate(d.getDate() + i);
            
            const dateStr = d.toISOString().split('T')[0];
            const isSelected = dateStr === selectedDateStr;
            
            // Randomize "Few Seats" or "Available" for UI purposes
            const statuses = ["● Few Seats", "● Available", "● WL 12"];
            const statusColor = isSelected ? "#28a745" : (i % 2 === 0 ? "#ff9800" : "#28a745");
            const status = statuses[Math.abs(i) % statuses.length];
            
            const dayName = dayNames[d.getDay()];
            const dayNum = String(d.getDate()).padStart(2, '0');
            
            slider.innerHTML += `
                <div class="date-item ${isSelected ? 'active' : ''}" onclick="changeDate('${dateStr}')">
                    <div class="mb-1">${dayName}, ${dayNum}</div>
                    <div style="font-size: 0.7rem; color: ${statusColor};">${status}</div>
                </div>
            `;
        }
    }

    // Calculate duration between departure and arrival times
    function calculateDuration(departureTime, arrivalTime) {
      const [depHours, depMinutes] = departureTime.split(':').map(part => parseInt(part));
      const [arrHours, arrMinutes] = arrivalTime.split(':').map(part => parseInt(part));
      
      let durationHours = arrHours - depHours;
      let durationMinutes = arrMinutes - depMinutes;
      
      if (durationMinutes < 0) {
        durationHours--;
        durationMinutes += 60;
      }
      
      if (durationHours < 0) {
        durationHours += 24; 
      }
      
      return `${durationHours}h ${durationMinutes}m`;
    }

    // Group trains by trainNumber
    function groupTrains(trainsData) {
        const grouped = {};
        trainsData.forEach(t => {
            if (!grouped[t.trainNumber]) {
                grouped[t.trainNumber] = {
                    trainNumber: t.trainNumber,
                    name: t.name,
                    departureTime: t.departureTime,
                    arrivalTime: t.arrivalTime,
                    source: t.source,
                    destination: t.destination,
                    date: t.date,
                    classes: []
                };
            }
            grouped[t.trainNumber].classes.push({
                classType: t.classType,
                price: t.price,
                date: t.date
            });
        });
        return Object.values(grouped);
    }

    function createTrainCard(train) {
        const duration = calculateDuration(train.departureTime, train.arrivalTime);
        
        let classesHTML = '';
        const classNames = {
            "2S": "2S", "SL": "SL", "CC": "CC", "3A": "3A", "2A": "2A", "1A": "1A"
        };
        
        train.classes.forEach((cls, index) => {
            // Simulate availability logic for UI
            const isAvailable = index % 3 !== 0; // Just for mockup variety
            const statusText = isAvailable ? "Available 0021" : "Not Available";
            const subText = isAvailable ? "Free Cancellation" : "No more booking";
            const statusClass = isAvailable ? "text-success" : "text-danger";
            const cardAvailableClass = isAvailable ? "available" : "unavailable";
            
            const tatkalBadge = (index % 2 === 0) ? `<span class="badge bg-success ms-1">Tatkal</span>` : ``;
            
            classesHTML += `
                <div class="class-card ${cardAvailableClass} me-3 p-2 rounded" onclick="bookTrain('${train.trainNumber}', '${train.name}', '${train.source}', '${train.destination}', '${train.date}', '${cls.classType}', '${train.departureTime}', '${train.arrivalTime}', '${cls.price}')">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <strong class="fs-6 theme-text">${classNames[cls.classType] || cls.classType} ${tatkalBadge}</strong>
                        <span class="fw-bold theme-text">₹${cls.price}</span>
                    </div>
                    <div class="${statusClass} fw-bold mb-1 availability-text">
                        ${statusText}
                    </div>
                    <small class="text-muted d-block" style="font-size:0.7rem;">${subText}</small>
                </div>
            `;
        });
        
        // Random update times for mockup
        const updatedAgo = Math.floor(Math.random() * 10) + 1;

        return `
            <div class="col-12 mb-4">
                <div class="train-main-card">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <div class="train-card-title theme-text">
                            ${train.trainNumber} ${train.name}
                        </div>
                        <div>
                            <i class="bi bi-cup-hot text-muted me-2" title="Pantry Available"></i>
                            <span class="badge bg-light text-dark border"><i class="bi bi-star text-warning"></i> 4.3</span>
                        </div>
                    </div>
                    
                    <div class="d-flex align-items-center mb-3">
                        <h5 class="mb-0 me-2 fw-bold theme-text">${train.departureTime} <span class="text-muted fs-6">${train.source}</span></h5>
                        <span class="text-muted mx-2" style="font-size:0.8rem;">--- ${duration} ---</span>
                        <h5 class="mb-0 ms-2 fw-bold theme-text">${train.arrivalTime} <span class="text-muted fs-6">${train.destination}</span></h5>
                        <a href="#" class="ms-auto text-decoration-underline text-primary" style="font-size:0.9rem;">Schedule</a>
                    </div>
                    
                    <div class="d-flex text-muted mb-2" style="font-size: 0.75rem; gap: 130px;">
                        <span>${updatedAgo} hrs ago</span>
                        <span>${updatedAgo+1} hrs ago</span>
                        <span>${updatedAgo+3} hrs ago</span>
                    </div>

                    <div class="d-flex flex-nowrap overflow-auto class-cards-container">
                        ${classesHTML}
                    </div>
                </div>
            </div>
        `;
    }

    function bookTrain(trainNumber, trainName, source, destination, date, classType, departureTime, arrivalTime, price) {
        const url = `bookings.html?train=${encodeURIComponent(trainNumber)}&trainName=${encodeURIComponent(trainName)}&source=${encodeURIComponent(source)}&destination=${encodeURIComponent(destination)}&date=${encodeURIComponent(date)}&classType=${encodeURIComponent(classType)}&departureTime=${encodeURIComponent(departureTime)}&arrivalTime=${encodeURIComponent(arrivalTime)}&price=${encodeURIComponent(price)}`;
        window.location.href = url;
    }

    async function fetchTrains() {
      const params = getUrlParams();
      const { source, destination, classType, date } = params;
      
      document.getElementById('source-station').textContent = source ? source : 'Source';
      document.getElementById('destination-station').textContent = destination ? destination : 'Destination';
      document.getElementById('source-name-title').textContent = source ? source : 'Source';
      document.getElementById('destination-name-title').textContent = destination ? destination : 'Destination';
      
      generateDateSlider(date);
      
      document.getElementById('loading').classList.remove('d-none');
      document.getElementById('trains-container').classList.add('d-none');
      document.getElementById('no-trains').classList.add('d-none');
      
      try {
        const queryParams = new URLSearchParams();
        if (source) queryParams.append('source', source);
        if (destination) queryParams.append('destination', destination);
        if (classType) queryParams.append('classType', classType);
        if (date) queryParams.append('date', date);
        
        // Fix: Use the current origin or relative path, rather than localhost:1301 which is the old Spring Boot port
        const response = await fetch(`/api/trains/search?${queryParams.toString()}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const flatTrains = await response.json();
        
        document.getElementById('loading').classList.add('d-none');
        
        if (flatTrains && flatTrains.length > 0) {
          const groupedTrains = groupTrains(flatTrains);
          document.getElementById('train-count').textContent = groupedTrains.length;
          
          document.getElementById('trains-container').classList.remove('d-none');
          const trainsHTML = groupedTrains.map(train => createTrainCard(train)).join('');
          document.getElementById('trains-container').innerHTML = trainsHTML;
          
          // Apply theme
          const currentTheme = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
          const themeTextElements = document.querySelectorAll('.theme-text');
          themeTextElements.forEach(el => {
            el.style.color = currentTheme === "dark" ? "#fff" : "#000";
          });
        } else {
          document.getElementById('no-trains').classList.remove('d-none');
        }
      } catch (error) {
        console.error('Error fetching trains:', error);
        document.getElementById('loading').classList.add('d-none');
        document.getElementById('no-trains').classList.remove('d-none');
        document.querySelector('#no-trains p').textContent = 'An error occurred while searching for trains. Please try again.';
      }
    }

    document.addEventListener('DOMContentLoaded', () => {
      const savedTheme = localStorage.getItem('theme') || 'light';
      setTheme(savedTheme);
      fetchTrains();
    });
"""
        content = content[:script_start] + new_script + content[script_end:]
    
    with open('static/trains.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated static/trains.html successfully")

if __name__ == '__main__':
    main()
