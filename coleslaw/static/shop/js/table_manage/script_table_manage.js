function editName(id, elem){
    customConfirm("수정 하시겠습니까?")
    .then((result) => {
        if (!result) {
            return false;
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
                customAlert('로그인 해주세요.');
            }
            else if(error.status == 403){
                customAlert('권한이 없습니다!');
            }
            else{
                customAlert(error.status + JSON.stringify(error.responseJSON));
            }
        },
    });
    });
}

function deleteTable(id){
    customConfirm("삭제 하시겠습니까?")
    .then((result) => {
        if (!result) {
            return false;
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
                customAlert(data.message, ()=>{
                    location.reload(true);
                });
            },
            error: function(error) {
                if(error.status == 401){
                    customAlert('로그인 해주세요.');
                }
                else if(error.status == 403){
                    customAlert('권한이 없습니다!');
                }
                else{
                    customAlert(error.status + JSON.stringify(error.responseJSON));
                }
            },
        });
    });
}