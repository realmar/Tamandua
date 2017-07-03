function mapper() {
    for(t in this.tags) {
        emit(this.tags[t], null);
    }
}