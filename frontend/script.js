// 1. Total Employees Chart
function createTotalEmployeesChart(data) {
    const weekCounts = {};
    data.forEach(item => {
        if (!weekCounts[item.Week]) {
            weekCounts[item.Week] = new Set();
        }
        weekCounts[item.Week].add(item.SOEID);
    });

    const weeks = Object.keys(weekCounts);
    const employeeCounts = weeks.map(week => weekCounts[week].size);

    const ctx = document.getElementById('totalEmployeesChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: weeks,
            datasets: [{
                label: 'Total Employees',
                data: employeeCounts,
                backgroundColor: 'rgba(54, 162, 235, 0.8)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Employees'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Week'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Total Employees per Week'
                }
            }
        }
    });
}

createTotalEmployeesChart(jsonData);


// 2. PTS Status by Resource Manager Chart and Table
function createPTSStatusByManagerChart(data) {
    const weekManagerStatusCounts = {};
    data.forEach(item => {
        if (!weekManagerStatusCounts[item.Week]) {
            weekManagerStatusCounts[item.Week] = {};
        }
        if (!weekManagerStatusCounts[item.Week][item.Resource_Manager]) {
            weekManagerStatusCounts[item.Week][item.Resource_Manager] = {};
        }
        if (!weekManagerStatusCounts[item.Week][item.Resource_Manager][item.PTS_Status]) {
            weekManagerStatusCounts[item.Week][item.Resource_Manager][item.PTS_Status] = 0;
        }
        weekManagerStatusCounts[item.Week][item.Resource_Manager][item.PTS_Status]++;
    });

    const weeks = Object.keys(weekManagerStatusCounts).sort((a, b) => { // Sort weeks chronologically if needed
        const weekAStartDate = new Date(jsonData.find(item => item.Week === a).Week_Start_Date);
        const weekBStartDate = new Date(jsonData.find(item => item.Week === b).Week_Start_Date);
        return weekAStartDate - weekBStartDate;
    });

    const resourceManagers = [...new Set(data.map(item => item.Resource_Manager))];
    const statusTypes = ['Submitted', 'Saved', 'Rejected']; // Ensure order

    const datasets = resourceManagers.flatMap(manager => {
        return statusTypes.map(status => {
            const dataPoints = weeks.map(week => {
                return weekManagerStatusCounts[week]?.[manager]?.[status] || 0;
            });
            return {
                label: `${manager} - ${status}`,
                data: dataPoints,
                backgroundColor: getStatusColor(status),
                borderColor: getStatusColor(status).replace('0.8', '1'),
                borderWidth: 1,
                stack: manager // Stack bars for each manager across different PTS statuses
            };
        });
    });


    const ctx = document.getElementById('ptsStatusByManagerChart').getContext('2d');
    const ptsStatusByManagerChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: weeks,
            datasets: datasets
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Employees'
                    },
                     stacked: true // Enable Y-axis stacking
                },
                x: {
                    title: {
                        display: true,
                        text: 'Week'
                    }
                },
            },
            plugins: {
                title: {
                    display: true,
                    text: 'PTS Status by Resource Manager per Week'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    const elementIndex = elements[0].index;
                    const datasetIndex = elements[0].datasetIndex;
                    const clickedWeek = weeks[elementIndex];
                    const clickedManager = resourceManagers[Math.floor(datasetIndex / statusTypes.length)]; // Correct Manager
                    const clickedStatus = statusTypes[datasetIndex % statusTypes.length]; // Correct Status
                    displayPTSStatusByManagerTable(jsonData, clickedWeek, clickedManager, clickedStatus);
                }
            }
        }
    });
}


function getStatusColor(status) {
    switch (status) {
        case 'Submitted': return 'rgba(75, 192, 192, 0.8)'; // Green
        case 'Saved': return 'rgba(255, 205, 86, 0.8)';     // Yellow
        case 'Rejected': return 'rgba(255, 99, 132, 0.8)';  // Red
        default: return 'rgba(153, 102, 255, 0.8)';        // Purple (default)
    }
}


function displayPTSStatusByManagerTable(data, week, manager, status) {
    const tableData = data.filter(item =>
        item.Week === week && item.Resource_Manager === manager && item.PTS_Status === status
    );

    const tableContainer = document.getElementById('ptsStatusByManagerTable');
    tableContainer.innerHTML = ''; // Clear previous table
    if (tableData.length === 0) {
        tableContainer.style.display = 'none';
        return; // No data, hide table and exit
    }

    const table = document.createElement('table');
    table.className = 'table table-bordered table-striped';

    // Table Header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    const headers = ['SOEID', 'Week', 'Resource Manager', 'PTS Status', 'Vendor', 'Resource Type', 'Hours Charged'];
    headers.forEach(headerText => {
        const th = document.createElement('th');
        th.textContent = headerText;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Table Body
    const tbody = document.createElement('tbody');
    tableData.forEach(item => {
        const row = document.createElement('tr');
        row.insertCell().textContent = item.SOEID;
        row.insertCell().textContent = item.Week;
        row.insertCell().textContent = item.Resource_Manager;
        row.insertCell().textContent = item.PTS_Status;
        row.insertCell().textContent = item.Vendor;
        row.insertCell().textContent = item.Resource_Type;
        row.insertCell().textContent = item.Hours_Charged;
        tbody.appendChild(row);
    });
    table.appendChild(tbody);

    tableContainer.appendChild(table);
    tableContainer.style.display = 'block'; // Show table
}


createPTSStatusByManagerChart(jsonData);


// 3. PTS Status Overview Chart (Pie Chart)
function createPTSStatusOverviewChart(data) {
    const statusCounts = {};
    data.forEach(item => {
        if (!statusCounts[item.PTS_Status]) {
            statusCounts[item.PTS_Status] = 0;
        }
        statusCounts[item.PTS_Status]++;
    });

    const statuses = Object.keys(statusCounts);
    const counts = statuses.map(status => statusCounts[status]);
    const colors = statuses.map(status => getStatusColor(status).replace('0.8', '0.9')); // Slightly darker colors for pie

    const ctx = document.getElementById('ptsStatusOverviewChart').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: statuses,
            datasets: [{
                label: 'PTS Status Overview',
                data: counts,
                backgroundColor: colors,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Overall PTS Status Distribution'
                },
                 tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed) {
                                label += context.parsed + ' (' + ((context.parsed / data.length) * 100).toFixed(1) + '%)';
                            }
                            return label;
                        }
                    }
                }
            },
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    const elementIndex = elements[0].index;
                    const clickedStatus = statuses[elementIndex];
                    displayPTSStatusOverviewTable(jsonData, clickedStatus);
                }
            }
        }
    });
}

function displayPTSStatusOverviewTable(data, status) {
    const tableData = data.filter(item => item.PTS_Status === status);
    const tableContainer = document.getElementById('ptsStatusOverviewTable');
    tableContainer.innerHTML = '';

     if (tableData.length === 0) {
        tableContainer.style.display = 'none';
        return;
    }

    const table = createDataTable(tableData); // Reuse function if possible
    tableContainer.appendChild(table);
    tableContainer.style.display = 'block';
}

createPTSStatusOverviewChart(jsonData);


// 4. PTS Status Trend Over Weeks (Line Chart)
function createPTSStatusTrendChart(data) {
    const weekStatusCounts = {};
    data.forEach(item => {
        if (!weekStatusCounts[item.Week]) {
            weekStatusCounts[item.Week] = {};
        }
        if (!weekStatusCounts[item.Week][item.PTS_Status]) {
            weekStatusCounts[item.Week][item.PTS_Status] = 0;
        }
        weekStatusCounts[item.Week][item.PTS_Status]++;
    });

    const weeks = Object.keys(weekStatusCounts).sort((a, b) => {
        const weekAStartDate = new Date(jsonData.find(item => item.Week === a).Week_Start_Date);
        const weekBStartDate = new Date(jsonData.find(item => item.Week === b).Week_Start_Date);
        return weekAStartDate - weekBStartDate;
    });
    const statusTypes = ['Submitted', 'Saved', 'Rejected'];
    const datasets = statusTypes.map(status => {
        return {
            label: `${status} Status`,
            data: weeks.map(week => weekStatusCounts[week]?.[status] || 0),
            borderColor: getStatusColor(status).replace('0.8', '1'),
            backgroundColor: getStatusColor(status).replace('0.8', '1'),
            borderWidth: 2,
            tension: 0.4 // For smoother lines
        };
    });

    const ctx = document.getElementById('ptsStatusTrendChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: weeks,
            datasets: datasets
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Employees'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Week'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'PTS Status Trend Over Weeks'
                }
            },
             onClick: (event, elements) => {
                if (elements.length > 0) {
                    const elementIndex = elements[0].index;
                    const datasetIndex = elements[0].datasetIndex;
                    const clickedWeek = weeks[elementIndex];
                    const clickedStatus = statusTypes[datasetIndex];
                    displayPTSStatusTrendTable(jsonData, clickedWeek, clickedStatus);
                }
            }
        }
    });
}


function displayPTSStatusTrendTable(data, week, status) {
    const tableData = data.filter(item => item.Week === week && item.PTS_Status === status);
    const tableContainer = document.getElementById('ptsStatusTrendTable');
    tableContainer.innerHTML = '';

     if (tableData.length === 0) {
        tableContainer.style.display = 'none';
        return;
    }

    const table = createDataTable(tableData); // Reuse function
    tableContainer.appendChild(table);
    tableContainer.style.display = 'block';
}

createPTSStatusTrendChart(jsonData);


// 5. Resource Type Breakdown Chart (Doughnut Chart)
function createResourceTypeBreakdownChart(data) {
    const resourceTypeCounts = {};
    data.forEach(item => {
        if (!resourceTypeCounts[item.Resource_Type]) {
            resourceTypeCounts[item.Resource_Type] = 0;
        }
        resourceTypeCounts[item.Resource_Type]++;
    });

    const resourceTypes = Object.keys(resourceTypeCounts);
    const counts = resourceTypes.map(type => resourceTypeCounts[type]);
    const colors = ['rgba(240, 128, 128, 0.8)', 'rgba(173, 216, 230, 0.8)']; // LightCoral, LightBlue

    const ctx = document.getElementById('resourceTypeBreakdownChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: resourceTypes,
            datasets: [{
                label: 'Resource Type Breakdown',
                data: counts,
                backgroundColor: colors,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top'
                },
                title: {
                    display: true,
                    text: 'Resource Type Distribution'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed) {
                                label += context.parsed + ' (' + ((context.parsed / data.length) * 100).toFixed(1) + '%)';
                            }
                            return label;
                        }
                    }
                }
            },
             onClick: (event, elements) => {
                if (elements.length > 0) {
                    const elementIndex = elements[0].index;
                    const clickedResourceType = resourceTypes[elementIndex];
                    displayResourceTypeBreakdownTable(jsonData, clickedResourceType);
                }
            }
        }
    });
}

function displayResourceTypeBreakdownTable(data, resourceType) {
    const tableData = data.filter(item => item.Resource_Type === resourceType);
    const tableContainer = document.getElementById('resourceTypeBreakdownTable');
    tableContainer.innerHTML = '';

     if (tableData.length === 0) {
        tableContainer.style.display = 'none';
        return;
    }

    const table = createDataTable(tableData); // Reuse function
    tableContainer.appendChild(table);
    tableContainer.style.display = 'block';
}


createResourceTypeBreakdownChart(jsonData);


// --- Helper Function to Create Table ---
function createDataTable(tableData) {
    const table = document.createElement('table');
    table.className = 'table table-bordered table-striped';

    // Table Header (assuming consistent keys across data objects)
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    const headers = Object.keys(tableData[0] || {}); // Get headers from first object
    headers.forEach(headerText => {
        const th = document.createElement('th');
        th.textContent = headerText;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Table Body
    const tbody = document.createElement('tbody');
    tableData.forEach(item => {
        const row = document.createElement('tr');
        headers.forEach(header => {
            row.insertCell().textContent = item[header] || ''; // Handle missing props
        });
        tbody.appendChild(row);
    });
    table.appendChild(tbody);
    return table;
}