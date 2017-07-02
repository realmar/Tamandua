function mapper() {
    for (var key in this) {
        emit(key, null);
    }
}