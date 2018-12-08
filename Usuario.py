class Usuario():
    _nombre=""
    _id=0
    _inicial = []
    _AsinList = []

    def getNombre(self):
        return self._nombre
    def setNombre(self, x):
        self._nombre = x

    def getId(self):
        return self._id
    def setId(self, x):
        self._id = x

    def getInitialList(self):
        return self._inicial
    def setInitialList(self, value):
        self._inicial.append(value)

    def getAsinList(self):
        return self._AsinList
    def setAsinList(self, value):
        self._AsinList.append(value)

    def borrarAsinList(self):
        del self._AsinList[:]
    def borrarInicialList(self):
        del self._inicial[:]
