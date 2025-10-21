const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;


function customAlert(message, callback = null) {
  const modalBody = document.getElementById("alertModalBody");
  modalBody.innerText = message;

  const alertModalElement = document.getElementById("alertModal");
  const alertModal = new bootstrap.Modal(alertModalElement);
  alertModal.show();

  // 포커스 이동
  alertModalElement.addEventListener(
    "shown.bs.modal",
    () => {
      alertModalElement.focus();
    },
    { once: true }
  );

  // 중복 방지용 핸들러 정의
  const handleEnter = (event) => {
    if (event.key === "Enter") {
      alertModal.hide();
    }
  };

  alertModalElement.addEventListener("keydown", handleEnter);

  // 모달 닫힐 때 핸들러 제거 및 콜백 실행
  const handleHidden = () => {
    alertModalElement.removeEventListener("keydown", handleEnter); // ⭐️ 리스너 정리
    if (callback) {
      callback();
    }
  };

  alertModalElement.addEventListener("hidden.bs.modal", handleHidden, {
    once: true,
  });
}


function customConfirm(message) {
  if (customConfirm.active) return Promise.resolve(false); // 이미 모달 열려있으면 무시
  customConfirm.active = true;

  return new Promise((resolve) => {
    const body = document.getElementById("confirmModalBody");
    const modalElement = document.getElementById("confirmModal");
    const modal = new bootstrap.Modal(modalElement);
    const okBtn = document.getElementById("confirmOk");
    const cancelBtn = document.getElementById("confirmCancel");

    body.innerText = message;
    modal.show();

    let handled = false;

    const handleOk = () => {
      if (handled) return;
      handled = true;
      modal.hide();
      resolve(true);
      cleanup();
    };

    const handleCancel = () => {
      if (handled) return;
      handled = true;
      modal.hide();
      resolve(false);
      cleanup();
    };

    const handleEnter = (event) => {
      if (handled) return;
      if (event.key === "Enter") {
        handled = true;
        modal.hide();
        resolve(true);
        cleanup();
      }
    };

    okBtn.addEventListener("click", handleOk);
    cancelBtn.addEventListener("click", handleCancel);
    modalElement.addEventListener("keydown", handleEnter);

    modalElement.addEventListener(
      "shown.bs.modal",
      () => {
        modalElement.focus();
      },
      { once: true }
    );

    function cleanup() {
      okBtn.removeEventListener("click", handleOk);
      cancelBtn.removeEventListener("click", handleCancel);
      modalElement.removeEventListener("keydown", handleEnter);
      customConfirm.active = false; // 모달 종료 시 플래그 해제
    }
  });
}
customConfirm.active = false;

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