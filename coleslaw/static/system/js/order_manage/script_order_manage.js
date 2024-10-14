const search_form = document.getElementById('search-form');

function SetNum(obj){
    val=obj.value;
    re=/[^0-9]/gi;
    obj.value=val.replace(re,""); 
}

function setAgency(){
    search_form.submit();
}

function setShop(){
    search_form.submit();
}