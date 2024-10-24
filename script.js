document.addEventListener("DOMContentLoaded", function () {
    // Charger les données des stations de vélo
    fetch('data/MMM_MMM_Velomagg.csv')
        .then(response => response.text())
        .then(data => {
            const rows = data.split('\n').slice(1); // Ignore l'en-tête
            const tableBody = document.querySelector('#stations tbody');
            rows.forEach(row => {
                const cols = row.split(',');
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${cols[0]}</td>
                    <td>${cols[1]}</td>
                    <td>${cols[5]}</td> <!-- Modifiez l'index en fonction de la structure du CSV -->
                `;
                tableBody.appendChild(tr);
            });
        })
        .catch(error => console.error('Erreur lors de la récupération des données:', error));
    
    // Code pour le graphique
    const ctx = document.getElementById('myChart').getContext('2d');
    const myChart = new Chart(ctx, {
        type: 'line', // Type de graphique
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'], // Modifiez ces étiquettes
            datasets: [{
                label: 'Trafic de Vélos',
                data: [12, 19, 3, 5, 2, 3], // Remplacez par vos données
                borderColor: 'rgba(75, 192, 192, 1)',
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
