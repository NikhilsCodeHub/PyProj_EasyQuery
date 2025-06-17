$('#topright > div:nth-child(2)').prepend(
    $('<img>', {
        id: 'newImage',
        src: '/images/smart_tip.svg',
        class: 'menuIcons newIcon',
        title: 'QnA Agent',
        click: function() {
                    $.ajax({
                        url: 'http://localhost:8123/tests/row_ai.html',  // Path to your HTML file
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
