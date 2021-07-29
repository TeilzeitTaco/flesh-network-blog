package com.fn.fleischchan.letters;

import com.fn.fleischchan.shared.FileModel;
import com.fn.fleischchan.shared.ImageStorageService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;


/**
 * API Definition
 */
@RestController
@RequestMapping("/api/v1/letters")
public class LetterController {
    private final LetterService letterService;
    private final ImageStorageService imageStorageService;

    @Autowired
    public LetterController(LetterService letterService, ImageStorageService imageStorageService) {
        this.letterService = letterService;
        this.imageStorageService = imageStorageService;
    }

    @GetMapping
    public Iterable<Letter> listLetters() {
        return letterService.listLetters();
    }

    @GetMapping("/{id}")
    public Letter get(@PathVariable("id") Integer id) {
        return letterService.getLetter(id);
    }

    @PostMapping
    public Letter create(@RequestBody Letter letter) {
        return letterService.save(letter);
    }

    @PutMapping("/{id}")
    public Letter put(@PathVariable("id") Integer id, @RequestBody Letter letter) {
        return letterService.save(letter);
    }

    /**
     * The frontend posts a [FileModel] to this endpoint to associate it with a letter.
     *
     * @param id ID of the letter
     * @param fileModel The FileModel
     * @return The letter after the modification
     */
    @PutMapping("/{id}/attachedImage")
    public Letter put(@PathVariable("id") Integer id, @RequestBody FileModel fileModel) {
        var letter = letterService.getLetter(id);
        if (!letter.hasAttachedImage()) {
            var realFileModel = imageStorageService.getFileModel(fileModel.getId());
            letter.setAttachedImage(realFileModel);
            letterService.save(letter);
        }

        return letter;
    }
}
