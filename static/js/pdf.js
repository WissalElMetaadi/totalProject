document.addEventListener('DOMContentLoaded', function () {
    const backgroundColors = [
        'rgba(255, 99, 132, 0.6)',
        'rgba(54, 162, 235, 0.6)',
        'rgba(255, 206, 86, 0.6)',
        'rgba(75, 192, 192, 0.6)',
        'rgba(153, 102, 255, 0.6)',
        'rgba(255, 159, 64, 0.6)',
        'rgba(199, 199, 199, 0.6)'
    ];
    const borderColors = [
        'rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)',
        'rgba(75, 192, 192, 1)', 'rgba(153, 102, 255, 1)', 'rgba(255, 159, 64, 1)',
        'rgba(159, 159, 159, 1)'
    ];
    const dateInput = document.getElementById('dateInput');

    const createChart = (ctx, type, data, options) => {
        return new Chart(ctx, {
            type: type,
            data: data,
            options: options
        });
    };

    const updateDataForVehicleChart = () => {
        const chosenDate = dateInput.value;
        fetch(`/data?date=${chosenDate}`)
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('vehicleChart').getContext('2d');
            if (window.myVehicleChart) window.myVehicleChart.destroy();
            window.myVehicleChart = createChart(ctx, 'bar', {
                labels: Object.keys(data),
                datasets: [{
                    label: 'Nombre de véhicules par classe',
                    data: Object.values(data),
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 1
                }]
            }, {
                responsive: true,
                maintainAspectRatio: false,
                scales: { 
                    y: { beginAtZero: true } 
                },
                legend: { 
                    display: true, 
                    position: 'top', 
                    labels: { 
                        fontColor: '#333', 
                        usePointStyle: true 
                    } 
                },
                title: { display: false }
            });
        });
    };

    const updateDataForHourlyChart = () => {
        const chosenDate = dateInput.value;
        fetch(`/data_par_heure?date=${chosenDate}`)
        .then(response => response.json())
        .then(allData => {
            const data = allData.vehicles_per_hour;
            const ctx = document.getElementById('vehiclesHourChart').getContext('2d');
            if (window.myChart) window.myChart.destroy();
            window.myChart = createChart(ctx, 'line', {
                labels: Object.keys(data),
                datasets: [{
                    label: 'Nombre total de véhicules par heure',
                    data: Object.values(data),
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    fill: false,
                }]
            }, {
                responsive: true,
                maintainAspectRatio: false,
                scales: { 
                    x: {
                        ticks: {
                            maxRotation: 0,
                            minRotation: 0
                        }
                    },
                    y: { 
                        beginAtZero: true 
                    }
                },
                layout: {
                    padding: {
                        left: 10,
                        right: 10,
                        top: 10,
                        bottom: 40
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            fontColor: '#333',
                            usePointStyle: true
                        }
                    },
                    title: {
                        display: false
                    }
                }
            });
        });
    };

    const updateDataForPumpUsageChart = () => {
        const chosenDate = dateInput.value;
        fetch(`/pump_data?date=${chosenDate}`)
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('pumpUsageChart').getContext('2d');
            if (window.myPumpUsageChart) window.myPumpUsageChart.destroy();
            window.myPumpUsageChart = createChart(ctx, 'pie', {
                labels: Object.keys(data),
                datasets: [{
                    label: 'Utilisation des Pompes',
                    data: Object.values(data),
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 1
                }]
            }, {
                responsive: true,
                maintainAspectRatio: false
            });
        });
    };

    const updateDataForAvgWaitTimeChart = () => {
        const chosenDate = dateInput.value;
        fetch(`/avg_wait_time_by_class?date=${chosenDate}`)
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('avgWaitTimeChart').getContext('2d');
            if (window.myAvgWaitTimeChart) window.myAvgWaitTimeChart.destroy();
            window.myAvgWaitTimeChart = createChart(ctx, 'bar', {
                labels: Object.keys(data),
                datasets: [{
                    label: 'Temps d\'attente moyen (en secondes)',
                    data: Object.values(data),
                    backgroundColor: 'rgba(153, 102, 255, 0.6)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1
                }]
            }, {
                responsive: true,
                maintainAspectRatio: false,
                scales: { 
                    y: { beginAtZero: true } 
                }
            });
        });
    };

    const updateTopClientsForDate = () => {
        const chosenDate = dateInput.value;
        if (chosenDate) {
            fetch(`/get-top-clients?date=${chosenDate}`)
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('pyramid-chart-container');
                container.innerHTML = '';
                data.sort((a, b) => b.value - a.value);
                data.forEach((item, index) => {
                    const barContainer = document.createElement('div');
                    barContainer.style.display = 'flex';
                    barContainer.style.alignItems = 'center';
                    barContainer.style.marginBottom = '10px';

                    const label = document.createElement('span');
                    label.textContent = `${item.label}: `;
                    label.style.minWidth = '100px';

                    const bar = document.createElement('div');
                    bar.style.height = '20px';
                    bar.style.width = `${Math.max(item.value, 1) * 10}px`;
                    bar.style.backgroundColor = index % 2 === 0 ? '#4e79a7' : '#f28e2b';
                    bar.textContent = item.value;
                    bar.style.color = 'white';
                    bar.style.display = 'flex';
                    bar.style.alignItems = 'center';
                    bar.style.justifyContent = 'center';
                    bar.style.textAlign = 'right';
                    bar.style.paddingRight = '5px';

                    barContainer.appendChild(label);
                    barContainer.appendChild(bar);
                    container.appendChild(barContainer);
                });
            });
        }
    };

    const loadData = (date) => {
        updateDataForVehicleChart(date);
        updateDataForHourlyChart(date);
        updateDataForPumpUsageChart(date);
        updateDataForAvgWaitTimeChart(date);
        updateTopClientsForDate(date);
    }

    // Set default date to 2024-04-05
    const defaultDate = '2024-04-05';
    dateInput.value = defaultDate;
    loadData(defaultDate);

    dateInput.addEventListener('change', () => {
        const chosenDate = dateInput.value;
        loadData(chosenDate);
    });

    // Fonction pour télécharger le PDF avec jsPDF
    document.getElementById('downloadPdf').addEventListener('click', function () {
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF();

        // Ajout des graphiques au PDF avec des tailles réduites et des titres
        pdf.setFontSize(16);
        pdf.text('Répartition des Véhicules par Classe dans la Journée', 15, 20);
        pdf.addImage(window.myVehicleChart.toBase64Image(), 'PNG', 15, 30, 180, 90);
        
        pdf.addPage();
        pdf.text('Nombre Total de Véhicules par Heure', 15, 20);
        pdf.addImage(window.myChart.toBase64Image(), 'PNG', 15, 30, 180, 90);
        
        pdf.addPage();
        pdf.text('Utilisation des Pompes', 15, 20);
        pdf.addImage(window.myPumpUsageChart.toBase64Image(), 'PNG', 15, 30, 180, 90);
        
        pdf.addPage();
        pdf.text('Temps d\'Attente Moyen par Classe de Véhicule', 15, 20);
        pdf.addImage(window.myAvgWaitTimeChart.toBase64Image(), 'PNG', 15, 30, 180, 90);

        // Télécharger le PDF
        pdf.save('rapport.pdf');
    });
});