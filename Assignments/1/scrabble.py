def largestAnagram():
    """the first function to be called. it produces an array of anagram groups and prints the largest one."""
    #open the dictionary
    dictionary = open("Dictionary.txt")
    #create a longest variable that keeps track of the longest entry from the dictionary. this will be required later when sorting the words.
    longest = 0
    #create an alphabetical array that will store words that have been counting sorted so that their letters are in alphabetical order
    alphabetical = []
    #iterate through all lines in the dictionary [O(N)]
    for line in dictionary:
        #remove newlines from the end of each entry to sterilize data input and make sure ord() values are correct
        line = line.replace('\n','')
        #keep track of longest word
        if len(line) > longest:
            longest = len(line)
        #append the countsorted version of the line to the alphabetical array, but retains the original version as well
        alphabetical.append([countSort(line), line])
    #iterate through each sorted element of the alphabetical array. the purpose of this loop is to make sure each one is the same length so that they can be radix sorted
    for i in range(len(alphabetical)):
        #if the word is not the longest, add the '`' character to the start of the string until its length is equal to the longest.
        if len(alphabetical[i][0]) < longest:
            alphabetical[i][0] = (longest-len(alphabetical[i][0]))*'`' + alphabetical[i][0] #'`' was chosen as its ord() value is one less than ord('a')
        i+=1
    #perform countsort longest times. this loop essentially performs a radix sort [O(N), called a constant number of times proportional to the longest word]
    for i in range(longest): #longest is a constant
        alphabetical = countForRadix(alphabetical, longest-1-i)
    #call the grouper function to group anagrams and return the array, longest group and its index
    [grouped, maximum, maxindex] = grouper(alphabetical)
    #print the largest group of anagrams. starts at index 1, as index 0 contains the modified string
    print("The largest anagram group is the " + str(grouped[maxindex][1])+ " group, with " + str(maximum-1) + " elements:")
    for i in range(1, len(grouped[maxindex])):
        print(grouped[maxindex][i])
    #call the menu function
    menu(grouped, longest)

def menu(array, longest):
    """the menu function asks the user for a query string until they type '***', at which point the loop terminates and processes halt."""
    #create a loop that runs while quit is False
    quit = False
    while not quit:
        query = input("Enter the query string: ")
        if query == "***":
            quit = True
        else:
            #countsort the string
            string = countSort(query)
            #find difference between query string and longest dictionary string. if difference is <0, then the query is longer than any entry, so no anagrams exist
            difference = longest-len(query)
            if difference < 0:
                print("No anagrams exist for " + query)
                continue
            #make the string as long as the longest entry so it will match the first element of its anagram group (if it exists)
            string = (difference)*'`'+string
            #call getScrabbleWords to find string
            index = getScrabbleWords(string, array)
            #if the index is None, no anagram group was found.
            if index is None:
                print("No anagrams exist for " + query)
            #if the length of the element at index is 2, then the query is the only word that can be made with its letters, i.e. there are no anagrams
            elif len(array[index]) == 2:
                print("No anagrams exist for " + query)
            else:
                #print the elements from 1 to N in the anagram group [O(W)]
                print("The anagrams for " + query + " are: ")
                for i in range(1, len(array[index])):
                    print(array[index][i])
            #if difference was 0, then no anagrams can exist with a wildcard as the query would be too long
            if difference == 0:
                print("and no anagrams exist with a wildcard.")
                continue
            else:
                print("without a wildcard.")
                #call getWildcardWords to find wildcard anagram groups
                words = getWildcardWords(query, array, difference)
                if len(words) == 0:
                    print('With a wildcard, no anagrams exist')
                else:
                    #print wildcard anagrams
                    print('With a wildcard anagrams are:')
                    for i in words:
                        print(i)



def countForRadix(array, index):
    """performs a modified version of countsort designed for use on dictionaries. can be called successively to produce a radix sort. index is the position of the letter to sort"""
    #create an output array 27 elements long [a-z and '`' values]
    output = [[] for _ in range(27)]
    #iterate through the array [O(N)]
    for i in range(len(array)):
        #find the value of the character
        value = ord(array[i][0][index])-96
        #increment the appropriate index
        output[value].append(array[i])
    #reset array
    array[:] = []
    #for each list in the output array, extend the array to contain all elements [O(N), as it must go through each entry]
    for containedList in output:
        array.extend(containedList)
    #return the new array
    return array


def grouper(array):
    """this function creates anagram groups according to similarity between adjacent elements on a radix sorted dictionary"""
    #create an output array 'grouped', keep track of the previous similar index and the largest anagram group and its index
    grouped = [['']]
    previous = 0
    maximum = 1
    maxindex = 0
    #iterate through each element of the array [O(N)]
    for current in range(0, len(array)):
        #if the next element in the array is equal to the previous element in grouped, they are anagrams, so append the word to the previous element in grouped
        if array[current][0] == grouped[previous][0]:
            grouped[previous].append(array[current][1])
            #keep track of the longest group
            if len(grouped[previous]) > maximum:
                maximum = len(grouped[previous])
                maxindex = previous
        #if they are not equal, move on to creating the next group
        else:
            previous += 1
            grouped.append(array[current])
    #return the grouped array and its maximum value and index
    return [grouped, maximum, maxindex]


def getScrabbleWords(string, array):
    """finds anagrams of a query string without wildcards. it is a binary search algorithm [O(logN)]"""
    #if the grouped array is empty, return None as there are no anagrams
    if len(array) == 0:
        return None
    #set lo to 0, hi to the last index and mid to the floor of their average
    lo = 0
    hi = len(array)-1
    mid = (hi+lo)//2
    #perform binary search on the strings. string comparison takes O(k), so total complexity of the function is O(klogN)
    while lo < hi-1:
        if string >= array[mid][0]:
            lo = mid
            mid = (lo+hi)//2
        elif string < array[mid][0]:
            hi = mid
            mid = (lo+hi)//2
        else:
            return mid
    #if the string at mid is correct, return mid as the index. otherwise return None
    if array[mid][0] == string:
        return mid
    else:
        return None

def getWildcardWords(string, array, difference):
    """finds wildcard anagrams by adding each letter of the alphabet to the query string and calling getScrabbleWords successively"""
    #store the ord() values for a and z
    aValue = ord('a')
    zValue = ord('z')
    words = []
    #for each ord value between ord(a) and ord(z), run this loop
    for value in range(aValue, zValue+1):   #runs a constant 26 times
        #add the letter, countsort the new string, then make up the difference between it and the longest entry with the '`' character'
        new_string = string + chr(value)
        new_string = countSort(new_string)
        new_string = (difference-1)*'`'+new_string #difference minus one because a letter is being added, so a character must be subtracted to keep length equal
        #find the anagram group with getScrabbleWords if it exists
        index = getScrabbleWords(new_string, array)
        if index == None:
            continue
        #append all found anagrams to the output array
        for i in range(1, len(array[index])): #in total, iterates a number proportional to the output (does not vary with N, but instead with number of anagrams found)
            words.append(array[index][i])
    #return output
    return words



def countSort(string):
    #find the overall value by creating a sum of the ord() values, then summing them
    values = [ord(c) for c in string]
    #create an array of the size of the maximum ord value (minus 96 to index a at 1)
    maximum = max(values) - 96
    #create an array to count the characters
    counts = [0] * maximum
    for a in string:
        #increment the appropriate index
        counts[ord(a)-97]+=1
    new_string = ""
    #reconstruct the string in order according to the count in each element of the counts array
    for c in range(len(counts)):
        new_string += chr(c+97)*counts[c]
    return new_string

largestAnagram()

