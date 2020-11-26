#![feature(assoc_char_funcs)]

use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;
//use math::round;

fn main() -> std::io::Result<()>{
    let mut longest = 0;

    let mut alphabetical = vec![];

    //alphabetical.push("testing".to_string());

    if let Ok(lines) = read_lines("./Dictionary.txt") {
        for line in lines {
            if let Ok(contents) = line {
                let trimmed = contents.replace("\n", "");
                if trimmed.len() > longest {
                    longest = trimmed.len();
                }
                alphabetical.push(vec![count_sort(&trimmed), trimmed]);
            }
        }
    }

    for i in 0..alphabetical.len() {
        if alphabetical[i][0].len() < longest {
            let discrepancy = longest - alphabetical[i][0].len();
            let mut append_string = (0..discrepancy).map(|_| "9").collect::<String>();
            append_string.push_str(&alphabetical[i][0]);
            alphabetical[i][0] = append_string;
        }
    }
    for i in 0..longest{
        alphabetical = count_for_radix(alphabetical, longest-i-1);
    }

    let (grouped, maximum, maxindex) = grouper(alphabetical);

   // println!("Grouped: {:?}, maximum: {}, maxindex: {}", grouped[maxindex], maximum, maxindex);

   println!("The largest anagram group is the {} group, with {} elements:", grouped[maxindex][1], maximum-1);
   for i in 1..grouped[maxindex].len(){
    println!("{}", grouped[maxindex][i]);
   }

    //println!("{:?}", alphabetical);
    menu(grouped, longest);
    Ok(())
}

fn menu(array: Vec<Vec<String>>, longest: usize) {
    loop {
        println!("Enter the query string: ");
        let mut query = String::new();
        io::stdin()
            .read_line(&mut query)
            .expect("Failed to read line.");

        query  = query.replace("\n", "");
            
        if query == "***".to_owned() {
            break;
        }
        println!("Your query string is {}", query);

        let string = count_sort(&query);
        let difference: i32 = (longest - query.len()) as i32;
        if (difference) < 0 {
            println!("No anagrams exist for {}", query);
            continue;
        }
        let mut append_string = (0..difference).map(|_| "9").collect::<String>();
        append_string.push_str(&string);

        if let Some(index) = get_scrabble_words(&append_string, &array) {
            if array[index].len() == 2 {
                println!("No anagrams exist for {}", query);
            }
            else {
                println!("The anagrams for {} are:", query);
                for string in array[index].iter() {
                    println!("{}", string);
                }
            }
        }
        else {
            println!("No anagrams exist for {}", query);
        }
        if difference == 0 {
            println!("and no anagrams exist with a wildcard.");
            continue;
        }
        else {
            println!("without a wildcard.");
            let words = get_wildcard_words(&query, &array, difference);
            if words.len() == 0 {
                println!("With a wildcard, no anagrams exist.");
                for word in words.iter() {
                    println!("{}", word);
                }
            }
            else {
                println!("With a wildcard, the anagrams are:");
                for word in words.iter() {
                    println!("{}", word);
                }
            }
        }

    }
}

fn get_scrabble_words(string: &str, array: &Vec<Vec<String>>) -> Option<usize> {
    if array.len() == 0 {
        return None; 
    }
    let mut lo = 0;
    let mut hi: usize = array.len() - 1;
    let mut mid: usize = (((hi + lo)/2) as f32).floor() as usize;

    while lo < hi - 1 {
        if string >= &array[mid][0] {
            lo = mid;
            mid = (((lo+hi)/2) as f32).floor() as usize;
        }
        else if string < &array[mid][0] {
            hi = mid;
            mid = (((lo+hi)/2) as f32).floor() as usize;
        }
        else{
            return Some(mid);
        }
    }
    if array[mid][0] == string {
        return Some(mid);
    }
    else {
        return None;
    }
}

fn get_wildcard_words(string: &str, array: &Vec<Vec<String>>, difference: i32) -> Vec<String> {
    let mut words = vec![];
    let alphabet = (b'a'..=b'z')
            .map(|c| c as char)
            .filter(|c| c.is_alphabetic())
            .collect::<Vec<_>>();
    for char in alphabet.iter() {
        let mut new_string = format!("{}{}", string, char);
        new_string = count_sort(&new_string);
        let mut append_string = (0..difference-1).map(|_| "9").collect::<String>();
        append_string.push_str(&new_string);
        if let Some(index) = get_scrabble_words(&append_string, &array) {
            for i in 1..array[index].len() {
                words.push(array[index][i].clone());
            }
        }
        else {
            continue;
        }
    }
    return words;
}

fn count_sort(string: &str) -> String{

    //println!("Current string is {}", string);

    let mut maximum = 0;

    for character in string.chars() {
        let encode = character.to_digit(36).unwrap() - 9;
        if encode > maximum {
            maximum = encode;
        }
    }

    //println!("Maximum is {}", maximum);

    let mut counts = vec![0; maximum as usize];
    //println!("Length of counts vector is {}", counts.len());
    for character in string.chars() {
        let index = character.to_digit(36).unwrap() - 10;
        counts[index as usize] += 1;
    }

    let mut new_string: String = "".to_owned();

    for i in 0..counts.len() {
        let append_char = char::from_digit(i as u32 + 10, 36).unwrap();
        let append_string = (0..counts[i]).map(|_| append_char).collect::<String>();
       // println!("Append char is {}, append string {}", append_char, append_string);
        // format!("{}{}", new_string, append_string);
        new_string.push_str(&append_string);

    }
    //println!("Total string is {}", new_string);
    return new_string.to_string();
}

fn read_lines<P> (filename: P) -> io::Result<io::Lines<io::BufReader<File>>>
where P: AsRef<Path>, {
    let file = File::open(filename)?;
    Ok(io::BufReader::new(file).lines())
}

fn count_for_radix(array: Vec<Vec<String>>, index: usize) -> Vec<Vec<String>> {
    let mut output = vec![vec![]; 27];
   // println!("Output is {:?}", output);
    for i in 0..array.len() {
        //println!("Character is {}", array[i][0].chars().nth(index).unwrap().to_digit(36).unwrap());
        let value = array[i][0].chars().nth(index).unwrap().to_digit(36).unwrap() - 9;
        //println!("Value is {}", value);
        
        output[value as usize].push(array[i].to_owned());

        }
    let mut return_array = vec![];
    for i in 0..output.len() {
        return_array.extend(output[i].to_owned());
    }
    //println!("Return array is {:?}", return_array);
    return return_array;
}

fn grouper(array: Vec<Vec<String>>) -> (Vec<Vec<String>>, u32, usize) {
    let mut grouped = vec![vec!['.'.to_string()]];
    let mut previous = 0;
    let mut maximum = 1;
    let mut maxindex = 0;

    for current_position in 0..array.len() {
        if array[current_position][0] == grouped[previous][0].to_string() {
            grouped[previous].push(array[current_position][1].to_owned());

            if grouped[previous].len() > maximum {
                maximum = grouped[previous].len();
                maxindex = previous;
            }
        }
        else {
            previous += 1;
            grouped.push(array[current_position].to_owned());
        }
    }

    return (grouped, maximum as u32, maxindex);
}