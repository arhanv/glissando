const uploadForm = document.getElementById('upload-form');
const message = document.getElementById('message');
const downloadButton = document.getElementById('download');

uploadForm.addEventListener('submit', function(event) {
  event.preventDefault();

  // Get the audio file and input text from the form
  const audioFile = document.getElementById('actual_btn').files[0];
  const inputText = document.getElementById('input-text').value;

  // Create a new FormData object and append the audio file and input text
  const formData = new FormData();
  formData.append('audio_file', audioFile);
  formData.append('input_text', inputText);

  // Send a POST request to the Flask route to process the audio file and input text
  fetch('/', {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    // Display the gpt_response variable on the page
    message.textContent = data.gpt_response;

    // Download the processed audio file as a file attachment
    const audioBlob = new Blob([data.audio_file_content], { type: 'audio/wav' });
    const audioUrl = URL.createObjectURL(audioBlob);
    const link = document.createElement('a');
    link.href = audioUrl;
    link.download = 'output.wav';
    document.body.appendChild(link);

    // Show the download button
    downloadButton.removeAttribute('hidden');

    // Add a click event listener to the download button to trigger the download
    downloadButton.addEventListener('click', function(event) {
      link.click();
    });
  })
  .catch(error => {
    console.error(error);
  });
});