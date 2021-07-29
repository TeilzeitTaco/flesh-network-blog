package com.fn.fleischchan.shared;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;


public interface FileRepository extends JpaRepository<FileModel, Integer> {
    Optional<FileModel> findFirstByHashOfContents(String hashOfContents);
}
