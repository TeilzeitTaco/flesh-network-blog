package com.fn.fleischchan.letters;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;


@Service
@Transactional(readOnly = true)
public class LetterService {
    private final LetterRepository letterRepository;

    @Autowired
    public LetterService(LetterRepository letterRepository) {
        this.letterRepository = letterRepository;
    }

    public Iterable<Letter> listLetters() {
        return letterRepository.findAllByOrderByTimestampDesc();
    }

    public Letter getLetter(Integer id) {
        return letterRepository.findById(id).orElse(null);
    }

    @Transactional
    public Letter save(Letter letter) {
        return letterRepository.save(letter);
    }

    @Transactional
    public Letter deleteLetter(Integer id) {
        var letter = letterRepository.findById(id).orElse(null);
        if (letter != null)
            letterRepository.delete(letter);

        return letter;
    }
}
