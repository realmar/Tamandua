function map() {
    function get(value) {
        try {
            emit(value<regex>, 1);
        }catch(e) {
            emit('', 1);
        }
    }

    if(this.<field> instanceof Array) {
        for(var i in this.<field>) {
            get(this.<field>[i])
        }
    }else{
        get(this.<field>)
    }
}