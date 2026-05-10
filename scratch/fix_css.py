def main():
    css = """
/* Specific Trains.html Styles */
.class-card {
    min-width: 140px;
    background-color: rgba(255, 255, 255, 0.7);
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid #ccc;
}
.class-card:hover {
    border-color: #0d6efd;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(13, 110, 253, 0.2);
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
    background: rgba(25, 30, 45, 0.7);
    backdrop-filter: blur(15px);
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 0 10px;
}
.date-slider {
    display: flex;
    overflow-x: auto;
    flex-grow: 1;
    scrollbar-width: none;
    scroll-behavior: smooth;
    -webkit-overflow-scrolling: touch;
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
    color: #ccc;
    transition: 0.3s;
}
.date-item:hover {
    background-color: rgba(255,255,255,0.05);
}
.date-item.active {
    border-bottom: 3px solid #28a745;
    color: #28a745;
    font-weight: bold;
}
.train-main-card {
    background: rgba(25, 30, 45, 0.7);
    backdrop-filter: blur(15px);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.5);
}
.train-card-title {
    font-size: 1.2rem;
    font-weight: bold;
    color: #fff;
}
.class-cards-container {
    padding-bottom: 10px;
}
.class-cards-container::-webkit-scrollbar {
    height: 6px;
}
.class-cards-container::-webkit-scrollbar-thumb {
    background-color: #555;
    border-radius: 10px;
}
.availability-text {
    font-size: 0.85rem;
}
.theme-text {
    color: #fff !important;
}

/* Loader */
.loader-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 50px;
}
.train-loader {
    font-size: 3rem;
    color: #0d6efd;
    animation: bounce 1s infinite;
}
@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-20px); }
}

.main-content {
    margin-top: 100px;
    padding: 20px 5%;
}
"""
    with open('static/common.css', 'a', encoding='utf-8') as f:
        f.write(css)
    print("Fixed common.css")

if __name__ == '__main__':
    main()
