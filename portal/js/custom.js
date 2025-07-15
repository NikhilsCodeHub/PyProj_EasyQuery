 questionhistory = []; // Array to store question history'
 console.log("loaded custom.js");
// -- clear the page when Clear button is clicked

  function clear() {
    // Clear the question input field
    $('#questionInput').val('');
    // Clear the DataTable
    if (dataTableInstance) {
      dataTableInstance.clear().draw();
    }
    // Hide messages and table
    $('#loadingMessage').hide();
    $('#OneLineMessage').hide();
    $('#errorMessage').hide();
    $('#tableContainer').hide();
    $("#tokenInfoText").text(''); // Clear token info text
    $("#tokenInfoSection").hide(); // Hide token info section
    // Clear the history list
    $('#historyList').empty();
    // Clear the question history array
    questionhistory = [];
    // Optionally, you can also reset the history ID counter if needed
    // Reset the history ID counter (if you want to start from 1 again)
    // questionhistory.length = 0; // Reset the length to 0
    // Alternatively, you can just reinitialize the array
    // questionhistory = []; // Reinitialize the array
    console.log("Cleared all data and reset the page.");
    // Optionally, you can update the UI or perform other actions here
    $('#errorMessage').text('All data cleared.').show();
  }

  function addToQnAHistory(question, query, columns, results, answer, token_info) {
    // Create a new entry for the question history
    const newEntry = {
      id: questionhistory.length + 1, // Incremental ID
      timestamp: new Date().toISOString(), // Current timestamp
      question: question,
      query: query,
      columns: columns, // Assuming columns is an array of column names
      result: results,
      answer: answer,
      token_info: token_info // Uncomment if you want to store token info
    };

    // Add the new entry to the history array
    questionhistory.push(newEntry);

    // Log the updated history for debugging
    //console.log("Updated QnA History:", questionhistory);
    console.log("Objects in QnA History:", questionhistory.length);
    // Optionally, you can update the UI or perform other actions here
    // For example, you could update a dropdown or a list to show the history
    const historyList = $('#historyList');
    historyList.empty(); // Clear existing items
    questionhistory.forEach((entry, index) => {
      historyList.append(`<li class="list-group-item list-group-item-action" style="cursor:pointer;border-bottom:2px solid gray;" onclick="showQnAHistory(${index})"><b>Q${entry.id}:</b> ${entry.question} (Rows ${entry.result.length})</li>`);
    });
  }

  function showQnAHistory(intHistoryId) {

    if (intHistoryId < 0 || intHistoryId >= questionhistory.length) {
      console.error("Invalid history ID:", intHistoryId);
      $('#errorMessage').text('Invalid history ID.').show();
      $('#tableContainer').hide();
      $('#loadingMessage').hide();
      $('#OneLineMessage').hide();
      $('#sqlQueryAccordion').hide(); // Clear the SQL Query display
      $('#sqlQueryText').text(''); // Clear the SQL Query text    
      return -1; // Return -1 for invalid ID
    }

    if (questionhistory[intHistoryId].result.length === 0) {
      $('#errorMessage').text('No data available for this question.').show();
      $('#tableContainer').hide();
      $('#OneLineMessage').hide();
      $('#loadingMessage').hide();
      $('#sqlQueryAccordion').show(); // Clear the SQL Query display
      //$('#sqlQueryText').text(''); // Clear the SQL Query text   
      return -1; // Return -1 for no data
    }
    if (questionhistory[intHistoryId].result.length > 1) {

    // Destroy existing DataTable instance if it exists
    if (dataTableInstance) {
      dataTableInstance.destroy();
    }
      $('#myDataTable thead').empty(); // Clear old headers
      $('#myDataTable tbody').empty(); // Clear old body
      $('#errorMessage').hide();
      $('#OneLineMessage').hide();
      $('#loadingMessage').show();
      $('#tableContainer').hide(); // Hide table while loading
      $('#sqlQueryAccordion').hide(); // Clear the SQL Query display
      $('#sqlQueryText').text(''); // Clear the SQL Query text   
    headers = questionhistory[intHistoryId].columns; // Assuming columns is an array of column names
    columns = headers.map(header => ({ title: header }));
    // Initialize DataTables with new data
    initializeDataTable(questionhistory[intHistoryId].result, columns);

    /* -- Commneted : Replaced with above function call --
    dataTableInstance = $('#myDataTable').DataTable({
      data: questionhistory[intHistoryId].result,
      columns: columns,
      paging: true,
      searching: true,
      ordering: true,
      info: true,
      destroy: true,
      layout: {
        topStart: {
            buttons: ['copy', 'csv', 'excel', 'pdf', 'print']
        }
        } // Allow re-initialization if needed later
    });
    */
    $('#loadingMessage').hide();
    $('#tableContainer').show(); // Show table after data is loaded
    $('#sqlQueryAccordion').show();
  }
    else if (questionhistory[intHistoryId].result.length === 1) {
      // Handle case where only one row is returned (e.g., no data)
      const answer = questionhistory[intHistoryId].answer.content;
      $('#loadingMessage').hide();
      $('#myDataTable').DataTable().clear().draw(); // Clear the table
      $('#OneLineMessage').text(answer).show();
      $('#errorMessage').hide();
      $('#tableContainer').hide();
      $('#sqlQueryAccordion').show();
    } 
    showTokenInfo(questionhistory[intHistoryId].token_info || {});
    return 1;
  }
 

 $(document).ready(function() {
      load_sidebar_dataset();
      

      $('#clearall').on('click', function() {
        clear();
      });
      // Reference to the DataTable instance
      dataTableInstance = null;
      console.log("Document is ready, initializing DataTable...");
      // Function to fetch data from the API and populate the table
      $('#submitQuestion').on('click', function() {
          
          const question = $('#questionInput').val();
          if (!question) {
              $('#errorMessage').text('Please enter a question.').show();
              $('#tableContainer').hide();
              return;
          }

          $('#loadingMessage').show();
          $('#OneLineMessage').hide();
          $('#errorMessage').hide();
          $('#tableContainer').hide(); // Hide table while loading
          $("#tokenInfoSection").hide();
          $('#sqlQueryAccordion').hide();
          $('#sqlQueryText').text('');

          // Replace 'YOUR_API_ENDPOINT' with the actual URL of your FastAPI endpoint
          // const apiEndpoint = 'http://localhost:7071/api/qna'; // e.g., 'http://127.0.0.1:8000/query' or whatever your FastAPI endpoint is
          const apiEndpoint = '/api/v2/qna';

          $.ajax({
              url: apiEndpoint,
              type: 'POST',
              contentType: 'application/json',
              data: JSON.stringify({ question: question }), // Send the question as JSON
              success: function(response) {
                  $('#loadingMessage').hide();
                  // console.log("API answer:", response.answer.content); // Log the entire response for debugging
                  console.log("API response:", response); // Log the entire response for debugging
                  //console.log("Result : ", response["result"])
                  if (response && response.result) {
                      const parsedData = response.result;

                      //console.log("Parsed Data:", parsedData.length); // Log parsed data for debugging
                      if ((parsedData && parsedData.length > 1) || (parsedData.length>0 && parsedData[0].length > 2)) {
                          // Extract headers (first row)
                          //const headers = parsedData.shift();
                          const headers = response.columns;

                          // Format headers for DataTables columns option
                          const columns = headers.map(header => ({ title: header }));

                          
                          // Destroy existing DataTable instance if it exists
                          if (dataTableInstance) {
                              dataTableInstance.destroy();
                              $('#myDataTable thead').empty(); // Clear old headers
                              $('#myDataTable tbody').empty(); // Clear old body
                            
                          }

                          // Initialize DataTables with new data
                          initializeDataTable(parsedData, columns);
/*                           --- Commented : Replaced with an initialize function call.
                          dataTableInstance = $('#myDataTable').DataTable({
                              data: parsedData,
                              columns: columns,
                              paging: true,
                              searching: true,
                              ordering: true,
                              info: true,
                              destroy: true, // Allow re-initialization if needed later
                              layout: {
                                  topStart: {
                                      buttons: ['copy', 'csv', 'excel', 'pdf', 'print']
                                  }
                              }
                          });
*/
                          $('#tableContainer').show(); // Show table after data is loaded
                      } else if (parsedData.length === 1) {
                          // Handle case where only one row is returned (e.g., no data)
                          const answer = response.answer.content || 'No data returned from the API.';
                          $('#loadingMessage').hide();
                          $('#myDataTable').DataTable().clear().draw(); // Clear the table
                          $('#OneLineMessage').text(answer).show();
                          $('#errorMessage').hide();
                          $('#tableContainer').hide();
                          $('#sqlQueryAccordion').show();
                      } else {
                          $('#errorMessage').text('No data returned from the API.').show();
                          $('#tableContainer').hide();
                          $('#sqlQueryAccordion').hide();
                      }
                      //console.log("Input Token Info: ", response.token_info.input_tokens);
                      //console.log("Parsed Data: ", parsedData[0].length);
                      addToQnAHistory(question, response.query, response.columns,response.result,response.answer, response.token_info);
                      showTokenInfo(response.token_info || {});
                  } else {
                      $('#errorMessage').text('Invalid API response format (missing "result" key).').show();
                      $('#tableContainer').hide();
                      $("#tokenInfoSection").hide();
                      $('#sqlQueryAccordion').hide();
                  }
              },
              error: function(jqXHR, textStatus, errorThrown) {
                  $('#loadingMessage').hide();
                  $('#errorMessage').text('API Error: ' + textStatus + ' - ' + errorThrown).show();
                  console.error("AJAX error:", textStatus, errorThrown, jqXHR.responseText);
                  $("#tokenInfoSection").hide();
                  $('#tableContainer').hide();
                  $('#sqlQueryAccordion').hide();
              }
          });
      });
   });

  function showTokenInfo(token_info) {
    // If token_info is a flat object with input_tokens/output_tokens, use directly
    if (typeof token_info.input_tokens !== 'undefined' && typeof token_info.output_tokens !== 'undefined') {
        $("#tokenInfoText").text(''); // Clear previous text'')');
        //console.log("Token Info:", token_info.input_tokens, " : ", token_info.output_tokens); // Log for debugging
        $("#tokenInfoText").text(`Input tokens: ${token_info.input_tokens}, Output tokens: ${token_info.output_tokens}`);
        $("#tokenInfoSection").show();
        $('#sqlQueryAccordion').show();
        return;
    }
    // Otherwise, sum tokens from all steps (write_query, extract_columns, generate_answer)
    // let total_input = 0;
    // let total_output = 0;
    // ["write_query", "extract_columns", "generate_answer"].forEach(function(key) {
    //     let usage = token_info[key];
    //     if (usage && usage.input_tokens !== undefined) total_input += parseInt(usage.input_tokens);
    //     if (usage && usage.output_tokens !== undefined) total_output += parseInt(usage.output_tokens);
    // });
    // $("#tokenInfoText").text(`Input tokens: ${total_input}, Output tokens: ${total_output}`);
    // $("#tokenInfoSection").show();
}



 // Update SQL query text when new QnA is added
  function updateSQLQuery(query) {
    $('#sqlQueryText').text(query || '');
  }

  // Hook into addToQnAHistory to update the SQL query display
  const originalAddToQnAHistory = addToQnAHistory;
  addToQnAHistory = function(question, query, columns, results, answer, token_info) {
    originalAddToQnAHistory.apply(this, arguments);
    updateSQLQuery(query);
  };

  // Also update when showing history
  const originalShowQnAHistory = showQnAHistory;
  showQnAHistory = function(intHistoryId) {
    const result = originalShowQnAHistory.apply(this, arguments);
    if (intHistoryId >= 0 && intHistoryId < questionhistory.length) {
      //console.log("Showing history for ID:", intHistoryId);
      //console.log("Query for history ID:", questionhistory[intHistoryId].query);
      updateSQLQuery(questionhistory[intHistoryId].query);
    }
    return result;
  };

  function initializeDataTable(data, columns) {
    /*
    // Guess numeric columns by checking the first row
    const sampleRow = data && data.length > 0 ? data[0] : [];
    const formattedColumns = columns.map((col, idx) => {
        // col may be an object ({title: ...}) or a string
        const colTitle = col.title || col;
        const isNumeric = sampleRow && !isNaN(parseFloat(sampleRow[idx])) && isFinite(sampleRow[idx]);
        if (isNumeric) {
            return {
                title: colTitle,
                render: function(data, type, row) {
                    if (data === null || data === undefined || data === '') return data;
                    const num = Number(data);
                    return isNaN(num) ? data : num.toFixed(2);
                }
            };
        } else {
            return { title: colTitle };
        }
    });

    // Destroy existing DataTable instance if it exists
    if (window.dataTableInstance) {
        window.dataTableInstance.destroy();
        $('#myDataTable thead').empty();
        $('#myDataTable tbody').empty();
    }
    */

    // Initialize DataTable
    window.dataTableInstance = $('#myDataTable').DataTable({
        data: data,
        columns: columns,
        paging: true,
        searching: true,
        ordering: true,
        info: true,
        destroy: true,
        layout: {
            topStart: {
                buttons: ['copy', 'csv', 'excel', 'pdf', 'print']
            }
        }
    });
}