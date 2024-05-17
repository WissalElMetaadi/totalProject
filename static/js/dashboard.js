
function updateTitle() {
    var governorate = document.getElementById('governorate').value;
    var stationId = document.getElementById('station-id').value;
    var titleElement = document.getElementById('station-title');
    titleElement.textContent = `${governorate} / ${stationId}`;
}

// Initialise le titre avec les valeurs par défaut
updateTitle();



// Fonction pour ouvrir des fenêtres de popup pour les images et modal


$(document).ready(function() {
// Initialisation de DataTables
var table = $('#example').DataTable({
"initComplete": function(settings, json) {
    $('input.datepicker').datepicker(); // Si vous utilisez jQuery UI Datepicker
}
});

// Ajustement de la largeur du conteneur de la table après initialisation
$('.dataTables_wrapper').css('width', '100%');

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

// Fonction de filtrage
function filterTable() {
var type = $('#type-filter').val();
var date = $('#date-filter').val();
console.log("Type filter value:", type);
console.log("Date filter value:", date);

table.column(10).search(type).draw();
table.column(5).search(date).draw();

console.log("Current search query for type:", table.column(10).search());
console.log("Current search query for date:", table.column(5).search());
}

// Attachement de l'événement de filtrage
$('#button-id').on('click', filterTable);
});

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



/*### MAP*/ 


function initializeMap() {
var tunisie = [36.83, 10.3];
var map = L.map('mapid').setView(tunisie, 6);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
attribution: '© OpenStreetMap contributors'
}).addTo(map);

var marker = L.marker(tunisie).addTo(map);
marker.bindPopup("<b>Tunisie</b>").openPopup();
// Nouvelles coordonnées pour les nouvelles places
var place1Coords = [37.04, 9.67];
var place2Coords = [34.88, 10.60];
var place3Coords = [33.87, 10.04];

// Ajout des marqueurs pour les nouvelles places
var markerPlace1 = L.marker(place1Coords).addTo(map);
markerPlace1.bindPopup("<b>Bizerte</b>").openPopup();

var markerPlace2 = L.marker(place2Coords).addTo(map);
markerPlace2.bindPopup("<b>Sfax</b>").openPopup();

var markerPlace3 = L.marker(place3Coords).addTo(map);
markerPlace3.bindPopup("<b>Gabes</b>").openPopup();


}
// Supposons que myVehicleChart est la référence globale à votre graphique
var myVehicleChart = null;

function updateDataForVehicleChart() {
const chosenDate = document.getElementById('dateInput').value;
// Définir des couleurs pour chaque classe de véhicules
const backgroundColors = [
'rgba(255, 99, 132, 0.6)', // Couleur pour la première classe
'rgba(54, 162, 235, 0.6)', // Couleur pour la deuxième classe
'rgba(255, 206, 86, 0.6)', // Couleur pour la troisième classe
'rgba(75, 192, 192, 0.6)', // Etc.
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

/* DEUXIEME CHART */
/* DEUXIEME CHART */
// Récupérer les données pour le deuxième graphique à partir de la nouvelle route
var myChart = null;
function updateDataForHourlyChart() {
const chosenDate = document.getElementById('dateInput').value;
console.log("Date choisie: ", chosenDate); // Afficher la date choisie

fetch(`/data_par_heure?date=${chosenDate}`)
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

function updateDataForPumpUsageChart() {
const chosenDate = document.getElementById('dateInput').value; // Récupérer la date choisie

// Modifier la requête fetch pour inclure la date choisie comme paramètre
fetch(`/pump_data?date=${chosenDate}`)
.then(response => response.json())
.then(data => {
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

/*4 eme chart*/
function updateDataForAvgWaitTimeChart() {
const chosenDate = document.getElementById('dateInput').value; // Récupérer la date choisie

// Inclure la date choisie dans la requête fetch
fetch(`/avg_wait_time_by_class?date=${chosenDate}`)
.then(response => response.json())
.then(data => {
const ctx = document.getElementById('avgWaitTimeChart').getContext('2d');

if (window.myAvgWaitTimeChart) {
    window.myAvgWaitTimeChart.destroy(); // Si un graphique existe déjà, le détruire
}

// Créer le nouveau graphique avec les données filtrées
window.myAvgWaitTimeChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: Object.keys(data),
        datasets: [{
            label: 'Temps d\'attente moyen (en secondes)',
            data: Object.values(data),
            backgroundColor: 'rgba(153, 102, 255, 0.6)',
            borderColor: 'rgba(153, 102, 255, 1)',
            borderWidth: 1
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
});
}



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


function updateTopClientsForDate() {
const chosenDate = document.getElementById('dateInput').value;
if (chosenDate) {

fetch(`/get-top-clients?date=${chosenDate}`)
.then(response => response.json())
.then(data => {
    console.log('****************',data)
    const container = document.getElementById('pyramid-chart-container');
    container.innerHTML = ''; // Clear previous content

    // Sort data to have the highest value at the top
    data.sort((a, b) => b.value - a.value);

    // Create horizontal bar chart segments
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
        bar.style.width = `${Math.max(item.value, 1) * 10}px`; // Adjust scale as necessary
        bar.style.backgroundColor = index % 2 === 0 ? '#4e79a7' : '#f28e2b'; // Alternate colors
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
})
.catch(error => console.error('Error fetching top clients:', error));
}
}













/*date*/
document.getElementById('dateInput').addEventListener('change', function() {
const chosenDate = this.value; // La date choisie par l'utilisateur
console.log(chosenDate); // Afficher la date choisie dans la console
updateDataForHourlyChart(chosenDate); 
updateDataForVehicleChart();// Fonction pour mettre à jour les données
updateDataForPumpUsageChart();
updateDataForAvgWaitTimeChart();
updateTopClientsForDate();
});

document.addEventListener('DOMContentLoaded', function() {
initializeMap();
});















document.addEventListener('DOMContentLoaded', function() {
const zoneButtons = document.querySelectorAll('.zone-tab');
const dateInput = document.getElementById('date-filter');
const filterButton = document.getElementById('filter-button');
const vehicleTypes = ["Small Truck", "Motorcycle", "Big Truck", "Car", "Taxi", "Construction Machine"];

zoneButtons.forEach(button => {
button.addEventListener('click', function() {
    zoneButtons.forEach(btn => btn.classList.remove('active'));
    this.classList.add('active');
    console.log('Zone selected:', this.getAttribute('data-zone'));
    fetchAndUpdateStats(this.getAttribute('data-zone'), dateInput.value);
});
});

filterButton.addEventListener('click', () => {
const activeZone = document.querySelector('.zone-tab.active').getAttribute('data-zone');
const selectedDate = dateInput.value;
console.log('Filter button clicked. Date:', selectedDate, 'Zone:', activeZone);
fetchAndUpdateStats(activeZone, selectedDate);
});

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
