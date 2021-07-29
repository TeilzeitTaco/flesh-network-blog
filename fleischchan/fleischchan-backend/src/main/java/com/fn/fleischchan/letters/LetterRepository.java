package com.fn.fleischchan.letters;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;


public interface LetterRepository extends JpaRepository<Letter, Integer> {
    Iterable<Letter> findAllByOrderByTitle();
    Iterable<Letter> findAllByOrderByTimestampDesc();
    Optional<Letter> findByTitle(String name);
}