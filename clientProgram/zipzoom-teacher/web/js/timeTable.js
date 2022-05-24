window.onload = async function(){
    if(localStorage.getItem('timeTable')){
        $('#table').DataTable( {        
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
            data: JSON.parse(localStorage.getItem('timeTable')),
            columns: [
                { data: 'period' },
                { data: 'subject', defaultContent:"-" },
                { data: 'zoom_url' }
            ]});

        document.getElementById('loading').style.display = 'none';

        return;
    }

    if(localStorage.getItem('classId')){
        var data = await eel.get_timeTable(JSON.parse(localStorage.getItem('classId')))();
        if(data['status'] === 'success'){
            data = data['data']['time_table'];
            var day = new Date().getDay();
            var dayArr = ['SUN','MON', 'TUE', 'WED', 'THU', 'FRI','SAT'];
            var todayTimeTable = [];
            data.map(row => {
                if(row.day == dayArr[day]){
                    todayTimeTable.push({'period': row.period, 'subject': row.subject, 'zoom_url': row.zoom_url? row.zoom_url : null});
                }
            });
            todayTimeTable.sort((a,b) => a.period - b.period);
            localStorage.setItem('timeTable', JSON.stringify(todayTimeTable));
            $('#table').DataTable( {        
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
                data: todayTimeTable,
                columns: [
                    { data: 'period' },
                    { data: 'subject', defaultContent:"-" },
                    { data: 'zoom_url' }
                ]});
        }
    }

}