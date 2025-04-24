const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;


function customAlert(message, callback = null) {
    const modalBody = document.getElementById("alertModalBody");
    modalBody.innerText = message;
  
    const alertModal = new bootstrap.Modal(document.getElementById("alertModal"));
    alertModal.show();

    if (callback) {
      // 모달이 닫힐 때 콜백 실행 (확인 버튼이든 ESC든, 바깥 클릭이든 다 포함)
      alertModalElement.addEventListener("hidden.bs.modal", () => {
          callback();
      }, { once: true }); // 한 번만 실행되게
  }
}

function customConfirm(message) {
    return new Promise((resolve) => {
      const body = document.getElementById("confirmModalBody");
      const modal = new bootstrap.Modal(document.getElementById("confirmModal"));
      const okBtn = document.getElementById("confirmOk");
      const cancelBtn = document.getElementById("confirmCancel");
  
      body.innerText = message;
      modal.show();
  
      // 기존 이벤트 제거 후 새로 등록
      okBtn.onclick = () => {
        modal.hide();
        resolve(true);
      };
      cancelBtn.onclick = () => {
        modal.hide();
        resolve(false);
      };
    });
  }


  function handleLogout(event) {
    event.preventDefault();  // 기본 href 동작을 막습니다.

    const url = event.target.getAttribute("data-url");  // data-url에서 URL을 가져옵니다.

    customConfirm("로그아웃 하시겠습니까?")
      .then((result) => {
        if (result) {
          // 사용자가 '확인'을 클릭한 경우, 로그아웃 URL로 이동합니다.
          window.location.href = url;
        }
      });
  }