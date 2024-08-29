const search_form = document.getElementById('search-form');

function selectYearMonth(){
    search_form.submit();
}

function xlsxDownload(type){
    if(!confirm("엑셀저장하시겠습니까?")){
        return false;
    }
    let url_search = new URLSearchParams(window.location.search);
    url_search.set(type, true);
    window.location.href = `?${url_search.toString()}`;
}