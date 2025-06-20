# Step1 : Add child node image for SQL QnA agent.

$('#topright > div:nth-child(2)').prepend(
    $('<img>', {
        id: 'newImage',
        src: '/images/smart_tip.svg',
        class: 'menuIcons newIcon',
        title: 'New Icon'
    })
);
$.ajax({
    url: 'http://localhost:8123/tests/row_ai.html',  // Path to your HTML file
    method: 'GET',
    dataType: 'html',          // Expecting HTML content
    success: function(data) {
        $("<div class='cardrow'></div>").html(data).insertAfter(document.all["kpiSection"].childNodes[1].childNodes[1]);  // Insert the HTML into the div
    },
    error: function(xhr, status, error) {
        console.error('Failed to load content:', error);
        $('#cardRow').html('<p>Error loading content.</p>');
    }
});

-- Load Dynamically via Console 
document.head.appendChild(Object.assign(document.createElement('script'), {src: 'https://192.168.86.39/tests/sideload.js', onload: () => console.log('Loaded!')}));

uvicorn simple_db_QnA.api_main:app --host 0.0.0.0 --port 443 --ssl-keyfile=simple_db_QnA/cert/key.pem --ssl-certfile=simple_db_QnA/cert/cert.pem

# Step2 : Add onClick event on the Agent Image.

# Step 3 : Load the javascript file which has functions to call Agent API
    - The javascript will render a panel with Textbox to ask questions. 
    - The javascript will display 2 buttons to submit question and cancel.
    - The javascript will show history of the questions asked, keep the result and query in the background.

# Step 4 : Add a Div node after the metrics bar called "div_agent". 

# Step 5: Display results on the page in a table inside the "div_agent".
