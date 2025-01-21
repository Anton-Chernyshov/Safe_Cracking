let timerDuration = 10 * 60; // 10 minutes in seconds
    const timerElement = document.getElementById("timer");

    // Function to format time in MM:SS
    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }

    // Function to start the countdown
    function startCountdown() {
        const interval = setInterval(() => {
            if (timerDuration <= 0) {
                clearInterval(interval);
                timerElement.textContent = "00:00"; // Timer ends at 0           
                alert("Time's up!");
                return;
            }

            timerElement.textContent = formatTime(timerDuration);
            timerDuration--;
        }, 1000); // Update every second
    }

    // Function to query the current timer value
    function getTimerValue() {
        return timerElement.textContent;
    }

    // Start the countdown when the page loads
    window.onload = startCountdown;