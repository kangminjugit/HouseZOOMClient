window.onload = async function(){
    // if(localStorage.getItem('studentTable')){
    //     console.log(JSON.parse(localStorage.getItem('studentTable')));
    //     $('#studentTable').DataTable( {        
    //         // 표시 건수기능 숨기기
    //         lengthChange: false,
    //         // 검색 기능 숨기기
    //         searching: false,
    //         // 정렬 기능 숨기기
    //         ordering: false,
    //         // 정보 표시 숨기기
    //         info: false,
    //         // 페이징 기능 숨기기
    //         paging: false, 
    //         data: JSON.parse(localStorage.getItem('studentTable')),
    //         columns: [
    //             { data: 'name' },
    //             { data: 'id'},
    //             { data: 'point' }
    //         ]});
    //     return;
    // }
    var data = await eel.get_studentTable(JSON.parse(localStorage.getItem('classId')), JSON.parse(localStorage.getItem('accessToken')))();
    if(data['status'] === 'success'){
        studentTable = data['data']['studentList'];
        console.log(studentTable);
        studentTable.sort((a,b) => a.name - b.name);
        localStorage.setItem('studentTable', JSON.stringify(studentTable));
        $('#studentTable').DataTable( {        
            // 표시 건수기능 숨기기
            lengthChange: false,
            // 검색 기능 숨기기
            searching: false,
            // 정렬 기능 숨기기
            ordering: false,
            // 정보 표시 숨기기
            info: false,
            // 페이징 기능 숨기기
            paging: false, 
            data: studentTable,
            columns: [
                { data: 'name' },
                { data: 'id'},
                { data: 'point' }
            ]});
    }

}


// $('.dataTable').on('click', 'tbody td', function() {

//     //get textContent of the TD
//     console.log('TD cell textContent : ', this.textContent)
  
//     //get the value of the TD using the API 
//     console.log('value by API : ', table.cell({ row: this.parentNode.rowIndex, column : this.cellIndex }).data());
//   })