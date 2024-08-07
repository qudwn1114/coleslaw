function editName(id, elem){
    if (!confirm("수정 하시겠습니까?")) {
        return;
    }
    let data = {id : id, table_name: document.getElementById(`table_${id}`).value};
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