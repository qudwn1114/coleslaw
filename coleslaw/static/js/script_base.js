const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;


function customAlert(message) {
    const modalBody = document.getElementById("alertModalBody");
    modalBody.innerText = message;
  
    const alertModal = new bootstrap.Modal(document.getElementById("alertModal"));
    alertModal.show();
}