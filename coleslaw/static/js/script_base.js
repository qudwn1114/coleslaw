const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;


function customAlert(message, callback = null) {
    const modalBody = document.getElementById("alertModalBody");
    modalBody.innerText = message;

    const alertModalElement = document.getElementById("alertModal");
    const alertModal = new bootstrap.Modal(alertModalElement);
    alertModal.show();


    // 모달이 열리고 나서 확인 버튼에 포커스
    alertModalElement.addEventListener('shown.bs.modal', () => {
      alertModalElement.focus();
    }, { once: true });

    if (callback) {
      // 모달이 닫힐 때 콜백 실행 (확인 버튼이든 ESC든, 바깥 클릭이든 다 포함)
      alertModalElement.addEventListener("hidden.bs.modal", () => {
          callback();
      }, { once: true }); // 한 번만 실행되게
  }
  // Enter 키로 확인 동작 추가 (콜백은 여기서 직접 실행하지 않음)
  alertModalElement.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
          alertModal.hide(); // 모달만 닫기, 콜백은 hidden 이벤트에서 처리
      }
  }, { once: true }); // 한번만 실행되게
}

function customConfirm(message) {
    return new Promise((resolve) => {
      const body = document.getElementById("confirmModalBody");
      const modalElement = document.getElementById("confirmModal");
      const modal = new bootstrap.Modal(modalElement);
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

      // 모달이 열리고 나서 확인 버튼에 포커스
      modalElement.addEventListener('shown.bs.modal', () => {
          modalElement.focus();
      }, { once: true });

      // Enter 키로 '확인' 동작 추가
      modalElement.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
          modal.hide(); // 모달 닫기
          resolve(true); // 확인
        }
      });
    });
  }

  function handleLogout(event) {
    event.preventDefault();  // 기본 href 동작을 막습니다.
    const url = event.currentTarget.getAttribute("data-url");  // data-url에서 URL을 가져옵니다.

    customConfirm("로그아웃 하시겠습니까?")
      .then((result) => {
        if (result) {
          // 사용자가 '확인'을 클릭한 경우, 로그아웃 URL로 이동합니다.
          window.location.href = url;
        }
      });
  }