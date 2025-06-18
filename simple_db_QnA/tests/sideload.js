document.head.appendChild(Object.assign(document.createElement('script'), {src: 'https://code.jquery.com/jquery-3.7.1.min.js'}));
document.head.appendChild(Object.assign(document.createElement('script'), {src: 'https://cdn.datatables.net/2.0.8/js/dataTables.min.js'}));

document.head.appendChild(Object.assign(document.createElement('link'), {href: 'https://cdn.datatables.net/2.0.8/css/dataTables.dataTables.min.css', rel: 'stylesheet', type: 'text/css'}));

$('#topright > div:nth-child(2)').prepend(
    $('<img>', {
        id: 'newImage',
        src: '/images/smart_tip.svg',
        class: 'menuIcons newIcon',
        title: 'QnA Agent',
        click: function() {
                    $.ajax({
                        url: 'https://192.168.86.39/tests/row_ai.html',  // Path to your HTML file
                        method: 'GET',
                        dataType: 'html',          // Expecting HTML content
                        success: function(data) {
                            $("<div class='cardRow'></div>").html(data).insertAfter(document.all["kpiSection"].childNodes[1].childNodes[1]);  // Insert the HTML into the div
                        },
                        error: function(xhr, status, error) {
                            console.error('Failed to load content:', error);
                            $('#cardRow').html('<p>Error loading content.</p>');
                        }
                    });
        }
    })
);
