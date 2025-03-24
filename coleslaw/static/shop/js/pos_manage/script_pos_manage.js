$(document).ready(function() {
    $("#pos").on("change", function() {
        let isChecked = $(this).is(":checked");
        let selectedPosId = $("#pos_id").val(); // pos_id 셀렉트 박스의 선택된 값
        if (confirm("해당 포스로 이용하시겠습니까?")) {
            $.ajax({
                url: "",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                type: "PUT",
                contentType: "application/json",
                data: JSON.stringify({
                    pos_id: selectedPosId, type: 'POS'
                }),
                success: function(data) {
                    location.reload();
                },
                error: function(error) {
                    $("#pos").prop("checked", !isChecked); // 원래 상태로 복구
                    if(error.status == 401){
                        alert('로그인 해주세요.');
                    }
                    else if(error.status == 403){
                        alert('권한이 없습니다!');
                    }
                    else{
                        alert(error.status + JSON.stringify(error.responseJSON));
                    }
                },
            });
        } else {
            $("#pos").prop("checked", !isChecked); // 사용자가 취소하면 체크 상태 복구
        }
    });

    // pos_id 셀렉트 박스 선택 시 페이지 이동
    $("#pos_id").on("change", function() {
        let selectedPosId = $(this).val();
        window.location.href = "?pos_id=" + selectedPosId; // 실제 페이지 URL로 변경
    });

    $("#pos_create").on("click", function() {
        let selectedPosId = $("#pos_id").val(); // pos_id 셀렉트 박스의 선택된 값
        window.location.href = create_url + "?pos_id=" + selectedPosId; // 실제 페이지 URL로 변경
    });
});



function editName(id, elem){
    if (!confirm("수정 하시겠습니까?")) {
        return;
    }
    let data = {id : id, type:'NAME', table_name: document.getElementById(`table_${id}`).value};
    elem.disabled=true;
    $.ajax({
        type: "PUT",
        url: "",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: JSON.stringify(data),
        datatype: "JSON",
        success: function(data) {
            location.reload();
        },
        error: function(error) {
            elem.disabled=false;
            if(error.status == 401){
                alert('로그인 해주세요.');
            }
            else if(error.status == 403){
                alert('권한이 없습니다!');
            }
            else{
                alert(error.status + JSON.stringify(error.responseJSON));
            }
        },
    });
}

function editTid(id, elem){
    if (!confirm("수정 하시겠습니까?")) {
        return;
    }
    let data = {id : id, type:'TID', tid: document.getElementById(`table_tid_${id}`).value};
    elem.disabled=true;
    $.ajax({
        type: "PUT",
        url: "",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: JSON.stringify(data),
        datatype: "JSON",
        success: function(data) {
            location.reload();
        },
        error: function(error) {
            elem.disabled=false;
            if(error.status == 401){
                alert('로그인 해주세요.');
            }
            else if(error.status == 403){
                alert('권한이 없습니다!');
            }
            else{
                alert(error.status + JSON.stringify(error.responseJSON));
            }
        },
    });
}



function deleteTable(id){
    if (!confirm("삭제 하시겠습니까?")) {
        return;
    }
    $.ajax({
        type: "DELETE",
        url: "",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: JSON.stringify({
            "id" : id
        }),
        datatype: "JSON",
        success: function(data) {
            alert(data.message);
            location.reload(true);
        },
        error: function(error) {
            if(error.status == 401){
                alert('로그인 해주세요.');
            }
            else if(error.status == 403){
                alert('권한이 없습니다!');
            }
            else{
                alert(error.status + JSON.stringify(error.responseJSON));
            }
        },
    });
}