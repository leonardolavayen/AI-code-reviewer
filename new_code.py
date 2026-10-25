def hasDuplicates(numeros):
    for i in range(len(numeros)):
        for j in range(len(numeros)):
            if i != j and numeros[i] == numeros[j]:
                return True
    return False



    