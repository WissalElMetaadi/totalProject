function updateTitle() {
    var governorate = document.getElementById('governorate').value;
    var stationId = document.getElementById('station-id').value;
    var titleElement = document.getElementById('station-title');
    titleElement.textContent = `${governorate} / ${stationId}`;
}

function updateTitleAndFilterData() {
    updateTitle();

    var governorate = document.getElementById('governorate').value;
    var station = document.getElementById('station-id').value;

    fetch('/filter_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ governorate: governorate, station: station })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Received data: ", data);  // Log the data to check if it is being received correctly

        // Clear existing table data
        $('#example').DataTable().clear().destroy();

        // Map the received data to the format expected by DataTables
        const tableData = data.map(row => ({
            track_id: row.track_id,
            class: row.class,
            license_plate_text: row.license_plate_text,
            score: row.score,
            pompes_info: row.pompes_info,
            date_entrée: row["date d'entrée"],
            date_sortie: row["date de sortie"],
            wait_time: row.wait_time,
            station_name: row.station_name || 'Unknown',
            car_image: row['Car Image'] ? `<a href="#" onclick="openImageWindow('${row['Car Image']}');">Voir Image du véhicule</a>` : 'Pas d\'image',
            license_plate_image: row['License Plate Image'] ? `<a href="#" onclick="openImageWindow('${row['License Plate Image']}');">Voir Image de la plaque</a>` : 'Pas d\'image',
            zone_total: row.ZoneTotal
        }));

        $('#example').DataTable({
            data: tableData,
            columns: [
                { data: 'track_id', defaultContent: '' },
                { data: 'class', defaultContent: '' },
                { data: 'license_plate_text', defaultContent: '' },
                { data: 'score', defaultContent: '' },
                { data: 'pompes_info', defaultContent: '' },
                { data: 'date d\'entrée', defaultContent: '' },
                { data: 'date de sortie', defaultContent: '' },
                { data: 'wait_time', defaultContent: '' },
                { data: 'station_name', defaultContent: 'Unknown' },
                { data: 'car_image', defaultContent: 'No image' },
                { data: 'license_plate_image', defaultContent: 'No image' },
                { data: 'zone_total', defaultContent: '' }
            ],
            "pageLength": 10
        });
        
    })
    .catch(error => console.error("Error fetching data: ", error));
}

document.addEventListener('DOMContentLoaded', (event) => {
    updateTitle();
    $('#example').DataTable({
        "pageLength": 10
    });
});















$(document).ready(function() {
    let lastCheckTime = Date.now();

    function updateNotification(messages) {
        const notificationMessages = $('#notificationMessages');
        const viewDetailsButton = $('#viewDetailsButton');

        console.log('Updating notifications with messages:', messages);

        notificationMessages.empty();

        messages.forEach(message => {
            const notificationElement = $('<p>').addClass('tnc-stat-value').text(message.text);
            notificationMessages.append(notificationElement);
        });

        if (messages.length > 0) {
            viewDetailsButton.show();
            viewDetailsButton.data('users', messages.map(msg => msg.user));
        } else {
            viewDetailsButton.hide();
        }
    }

    $('#viewDetailsButton').click(function() {
        const users = $(this).data('users');
        const userDetailsBody = $('#userDetailsBody');
        userDetailsBody.empty();

        users.forEach(user => {
            const userDetails = `
                <p><strong>Nom:</strong> ${user.name}</p>
                <p><strong>Email:</strong> ${user.email}</p>
                <p><strong>Genre:</strong> ${user.gender}</p>
                <p><strong>Type de Travailleur:</strong> ${user.worker_type}</p>
                <p><strong>Date de Naissance:</strong> ${user.birthdate}</p>
                <p><strong>Station:</strong> ${user.station_name}</p>
                <p><strong>gouvernorat:</strong> ${user.governorate_name}</p>

                <p><strong>CIN:</strong> ${user.cin}</p>
                <hr>
            `;
            userDetailsBody.append(userDetails);
        });

        openModal();
    });

    function fetchRecentUsers() {
        $.ajax({
            type: 'GET',
            url: '/get_recent_users',
            data: { since: lastCheckTime / 1000 },
            success: function(users) {
                console.log('Fetched recent users:', users);
                if (users.length > 0) {
                    const messages = users.map(user => ({
                        text: `Nouveau ${user.worker_type} ajouté à ${user.station_name}`,
                        user: user
                    }));
                    updateNotification(messages);
                    lastCheckTime = Date.now(); // Update the last check time
                } else {
                    console.log('No new users found');
                }
            },
            error: function(response) {
                console.error('Failed to fetch recent users', response);
            }
        });
    }

    setInterval(fetchRecentUsers, 5000);
});

function openModal() {
    console.log('Opening modal');
    const modal = document.getElementById('userDetailsModal');
    modal.classList.add('show');
}

function closeModal() {
    console.log('Closing modal');
    const modal = document.getElementById('userDetailsModal');
    modal.classList.remove('show');
}

document.getElementById('viewDetailsButton').addEventListener('click', openModal);
document.querySelector('.tnc-close').addEventListener('click', closeModal);

// Met à jour le titre de la station avec les valeurs de la région et de l'identifiant de station
function updateTitle() {
    var governorate = document.getElementById('governorate').value;
    var stationId = document.getElementById('station-id').value;
    var titleElement = document.getElementById('station-title');
    titleElement.textContent = `${governorate} / ${stationId}`;
}

// Initialise le titre avec les valeurs par défaut
updateTitle();

$(document).ready(function() {
    // Vérifiez si la table a déjà été initialisée
    if (!$.fn.DataTable.isDataTable('#example')) {
        // Initialisation de DataTables
        var table = $('#example').DataTable({
            "initComplete": function(settings, json) {
                // Initialise le datepicker sur les éléments input avec la classe .datepicker
                $('input.datepicker').datepicker(); // Si vous utilisez jQuery UI Datepicker
            }
        });

        // Ajustement de la largeur du conteneur de la table après initialisation
        $('.dataTables_wrapper').css('width', '70%');

        // Événement de clic pour ouvrir des images en popup
        $('#example tbody').on('click', 'td a.image-link', function(e) {
            e.preventDefault();
            var url = $(this).attr('href');
            openImageWindow(url);
        });

        // Fonction pour ouvrir des fenêtres de popup pour les images
        function openImageWindow(url) {
            var newWindow = window.open(url, 'ImagePopup', 'width=600,height=400');
            if (newWindow) {
                newWindow.focus();
            } else {
                alert('La fenêtre popup a été bloquée par le navigateur.');
            }
        }

        // Fonction de filtrage de la table
        function filterTable() {
            var type = $('#type-filter').val();
            var date = $('#date-filter').val();
            console.log("Type filter value:", type);
            console.log("Date filter value:", date);

            // Filtre la colonne 10 pour le type et la colonne 5 pour la date
            table.column(10).search(type).draw();
            table.column(5).search(date).draw();

            console.log("Current search query for type:", table.column(10).search());
            console.log("Current search query for date:", table.column(5).search());
        }

        // Attachement de l'événement de filtrage au bouton de filtrage
        $('#button-id').on('click', filterTable);

        // Lorsqu'un track_id est cliqué
        $('#example tbody').on('click', 'td a.track-info', function(e) {
            e.preventDefault();
            var tr = $(this).closest('tr');

            // Log pour déboguer
            console.log("Clic sur track_id détecté");

            // Obtenez les données textuelles des cellules
            var data = tr.find('td').map(function(index, td) {
                if (index === 8 || index === 9) { // Les indices doivent correspondre aux cellules contenant les liens des images
                    var imageUrl = $(td).find('a').attr('href');
                    console.log("URL de l'image trouvé à l'indice " + index + ": " + imageUrl);
                    return imageUrl;
                } else {
                    return $(td).text();
                }
            }).get();

            // Logs pour déboguer
            console.log("Données récupérées de la ligne: ", data);

            // Remplir la modale avec les données de la ligne
            $('#modalTrackId').text(data[0]);
            $('#modalClass').text(data[1]);
            $('#modalLPText').text(data[2]);
            $('#modalScoreLP').text(data[3]);
            $('#modalEntryDate').text(data[5]);
            $('#modalExitDate').text(data[6]);
            $('#modalWaitTime').text(data[7]);

            // Logs pour déboguer
            console.log("Image du véhicule URL: " + data[8]);
            console.log("Image de la plaque URL: " + data[9]);

            // Mettez à jour les sources des images dans la modale avec les URL récupérées
            $('#modalCarImage').attr('src', data[8]);
            $('#modalPlateImage').attr('src', data[9]);

            // Afficher la modale
            $('#detailsModal').show();
        });

        // Lorsque l'utilisateur clique sur (x), fermer la modale
        $('.close').on('click', function() {
            $('#detailsModal').hide();
        });

        // Lorsque l'utilisateur clique en dehors de la modale, la fermer
        $(window).on('click', function(event) {
            if ($(event.target).hasClass('modal')) {
                $('#detailsModal').hide();
            }
        });
    } else {
        console.warn("DataTable a déjà été initialisée.");
    }
});


// Lorsque l'utilisateur clique en dehors de la modale, la fermer
$(window).on('click', function(event) {
if ($(event.target).hasClass('modal')) {
$('#detailsModal').hide();
}
});

//#########################################################################################

// Gestion des graphiques et des cartes
document.addEventListener('DOMContentLoaded', function() {
    // Initialisation des graphiques
    initializeCharts();
});


//##############################################################################
// Supposons que myVehicleChart est la référence globale à votre graphique
var myVehicleChart = null;

// Mise à jour des données pour le graphique des véhicules
function updateDataForVehicleChart() {
    const chosenDate = document.getElementById('dateInput').value;

    // Définir des couleurs pour chaque classe de véhicules
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

    fetch(`/data?date=${chosenDate}`)
    .then(response => response.json())
    .then(data => {
        const ctx = document.getElementById('vehicleChart').getContext('2d');

        // Si un graphique existe déjà, le détruire
        if (myVehicleChart) {
            myVehicleChart.destroy();
        }

        // Créer le nouveau graphique avec les données mises à jour
        myVehicleChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    label: 'Nombre de véhicules par classe',
                    data: Object.values(data),
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
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
}

// Récupérer les données pour le graphique par heure
var myChart = null;
function updateDataForHourlyChart() {
    const chosenDate = document.getElementById('dateInput').value;
    console.log("Date choisie: ", chosenDate); // Afficher la date choisie

    fetch(`/data_par_heure1?date=${chosenDate}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Réponse réseau non OK');
        }
        return response.json();
    })
    .then(allData => {
        console.log("Données reçues: ", allData); // Afficher les données reçues

        const data = allData.vehicles_per_hour;
        const ctx = document.getElementById('vehiclesHourChart').getContext('2d');
        // Si un graphique existe déjà, détruisez-le
        if (myChart) {
            myChart.destroy();
        }
        // Générer le graphique
        myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    label: 'Nombre total de véhicules par heure',
                    data: Object.values(data),
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    fill: false,
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        console.log("Graphique mis à jour pour la date: ", chosenDate); // Confirmer la mise à jour du graphique
    })
    .catch(error => {
        console.error('Erreur lors de la récupération des données:', error);
    });
}

// Mise à jour des données pour le graphique d'utilisation des pompes
function updateDataForPumpUsageChart() {
    const chosenDate = document.getElementById('dateInput').value; // Récupérer la date choisie
    console.log(`Date choisie : ${chosenDate}`);

    // Modifier la requête fetch pour inclure la date choisie comme paramètre
    fetch(`/pump_data?date=${chosenDate}`)
    .then(response => response.json())
    .then(data => {
        console.log(`Données reçues du backend :`, data);
        const ctx = document.getElementById('pumpUsageChart').getContext('2d');

        // Si un graphique existe déjà, détruisez-le
        if (window.myPumpUsageChart) {
            window.myPumpUsageChart.destroy();
        }

        // Générer le nouveau graphique avec les données mises à jour
        window.myPumpUsageChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    label: 'Utilisation des Pompes',
                    data: Object.values(data),
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(153, 102, 255, 0.6)',
                        'rgba(104, 2, 2 ,0.6)',
                        'rgba(144, 148, 151,0.6)',
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(136, 122, 6 ,1)',
                        'rgba(144, 148, 151,1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                // Début du dessin du graphique en degrés, -90 pour commencer du haut
            }
        });
    })
    .catch(error => console.error('Erreur lors de la récupération des données:', error));
}


// Mise à jour des données pour le graphique de temps d'attente moyen
function updateDataForAvgWaitTimeChart() {
    const chosenDate = document.getElementById('dateInput').value; // Récupérer la date choisie
}
//#####################################################################################################
// Initialisation avec la date par défaut
document.addEventListener('DOMContentLoaded', function() {
    var defaultDate = '2024-04-05'; // Date par défaut
    var storedDate = localStorage.getItem('selectedDateInput');
    var dateToSet = storedDate ? storedDate : defaultDate;

    document.getElementById('dateInput').value = dateToSet;

    // Appeler les fonctions de mise à jour avec la date chargée
    updateDataForHourlyChart(dateToSet);
    updateDataForVehicleChart();
    updateTopClientsForDate();
    updateStatistics(dateToSet); // Mise à jour des statistiques avec la date initiale

    document.getElementById('dateInput').addEventListener('change', function() {
        const chosenDate = this.value; // La date choisie par l'utilisateur
        console.log(chosenDate); // Afficher la date choisie dans la console
        localStorage.setItem('selectedDateInput', chosenDate); // Sauvegarder la date dans le localStorage
        updateDataForHourlyChart(chosenDate);
        updateDataForVehicleChart();
        updateTopClientsForDate();
        updateStatistics(chosenDate); // Mise à jour des statistiques lorsque la date change
    });
});

function updateStatistics(selectedDate) {
    fetch('/api/statistics?date=' + selectedDate)
        .then(response => response.json())
        .then(data => {
            document.querySelector('.total-unique .number-unique').innerText = data.total_vehicules;
            document.querySelector('.vehicules-unique .number-unique').innerText = data.debit_ouvrable;
            document.querySelector('.taxis-unique .number-unique').innerText = data.debit_taxi;
            document.querySelector('.pl-unique .number-unique').innerText = data.debit_vl; // Débit VL
            document.querySelector('.capture-unique .number-unique').innerText = data.debit_pl; // Débit PL
        })
        .catch(error => console.error('Erreur lors de la récupération des statistiques:', error));
}


// Mise à jour des données pour les meilleurs clients en fonction de la date
function updateTopClientsForDate() {
    const chosenDate = document.getElementById('dateInput').value;
    if (chosenDate) {
        fetch(`/get-top-clients1?date=${chosenDate}`)
        .then(response => response.json())
        .then(data => {
            console.log('****************', data);
            const container = document.getElementById('pyramid-chart-container');
            container.innerHTML = ''; // Clear previous content

            // Sort data to have the highest value at the top
            data.sort((a, b) => b.value - a.value);

            // Create horizontal bar chart segments
            data.forEach((item, index) => {
                const barContainer = document.createElement('div');
                barContainer.classList.add('client-info');

                const label = document.createElement('span');
                label.textContent = `${item.label}: `;
                label.classList.add('client-id');

                const bar = document.createElement('div');
                bar.classList.add('client-data');
                bar.style.width = `${Math.max(item.value, 1) * 10}px`; // Adjust scale as necessary
                bar.textContent = item.value;

                barContainer.appendChild(label);
                barContainer.appendChild(bar);

                container.appendChild(barContainer);
            });
        })
        .catch(error => console.error('Error fetching top clients:', error));
    }
}
//#######################################################################################
document.addEventListener('DOMContentLoaded', function() {
    const zoneButtons = document.querySelectorAll('.zone-tab');
    const dateInput = document.getElementById('date-filter');
    const filterButton = document.getElementById('filter-button');
    const vehicleTypes = ["Small Truck", "Motorcycle", "Big Truck", "Car", "Taxi", "Construction Machine"];

    // Gestion des boutons de zones
    zoneButtons.forEach(button => {
        button.addEventListener('click', function() {
            zoneButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            console.log('Zone selected:', this.getAttribute('data-zone'));
            fetchAndUpdateStats(this.getAttribute('data-zone'), dateInput.value);
        });
    });

    // Gestion du bouton de filtrage
    filterButton.addEventListener('click', () => {
        const activeZone = document.querySelector('.zone-tab.active').getAttribute('data-zone');
        const selectedDate = dateInput.value;
        console.log('Filter button clicked. Date:', selectedDate, 'Zone:', activeZone);
        fetchAndUpdateStats(activeZone, selectedDate);
    });

    // Fonction pour récupérer et mettre à jour les statistiques
    function fetchAndUpdateStats(zone, date) {
        console.log('Fetching data for zone:', zone, 'and date:', date);
        fetch(`/api/data?zone=${zone}&date=${date}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.message);
            } else {
                console.log('Data received:', data);
                vehicleTypes.forEach(type => {
                    const elementId = `${type.toLowerCase().replace(' ', '-')}-value`;
                    const element = document.getElementById(elementId);
                    if (element) {
                        element.textContent = data[type] || 0;
                        console.log(`Updated ${type} value: ${data[type]}`);
                    } else {
                        console.error(`Element with id ${elementId} not found.`);
                    }
                });
            }
        })
        .catch(error => console.error('Error fetching data:', error));
    }

    // Initialiser avec la première zone par défaut
    fetchAndUpdateStats('Pompe', '');
});

// Fonction pour afficher une zone spécifique
function showZone(zone) {
    const statContainers = document.querySelectorAll('.zone');
    statContainers.forEach(container => {
        if (container.getAttribute('data-zone') === zone) {
            container.style.display = 'flex';
        } else {
            container.style.display = 'none';
        }
    });
}
//#######################################################
document.addEventListener("DOMContentLoaded", function () {
    var categories = document.querySelectorAll(".category > li > a");

    categories.forEach(function (category) {
        category.addEventListener("click", function (event) {
            event.preventDefault();

            var subcategory = this.nextElementSibling;

            // Check if the clicked category is already open
            if (subcategory && subcategory.style.display === "block") {
                subcategory.style.display = "none";
            } else {
                // Close all other open subcategories
                document.querySelectorAll(".subcategory").forEach(function (subcat) {
                    subcat.style.display = "none";
                });

                // Open the clicked category's subcategory
                if (subcategory) {
                    subcategory.style.display = "block";
                }
            }
        });
    });
});
//#########################################################################
