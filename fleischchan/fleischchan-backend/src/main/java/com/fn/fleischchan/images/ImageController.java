package com.fn.fleischchan.images;

import com.fn.fleischchan.exceptions.StorageFileNotFoundException;
import com.fn.fleischchan.shared.FileModel;
import com.fn.fleischchan.shared.ImageStorageService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.security.NoSuchAlgorithmException;


@Controller
@RequestMapping("/api/v1/files")
public class ImageController {
    private final ImageStorageService imageStorageService;

    @Autowired
    public ImageController(ImageStorageService imageStorageService) {
        this.imageStorageService = imageStorageService;
    }

    @GetMapping("/{id}")
    @ResponseBody
    public FileModel get(@PathVariable("id") Integer id) {
        return imageStorageService.getFileModel(id);
    }

    @GetMapping("/{hashOfContents:.+}/content")
    @ResponseBody
    public ResponseEntity<Resource> serveFileViaHash(@PathVariable String hashOfContents) throws StorageFileNotFoundException {
        // Exists so that front-end caching is the best it can be
        var fileModel = imageStorageService.getFileModel(hashOfContents);
        return processFileModel(fileModel);
    }

    @GetMapping("/{id:\\d+}/content")
    @ResponseBody
    public ResponseEntity<Resource> serveFileViaId(@PathVariable("id") Integer id) throws StorageFileNotFoundException {
        var fileModel = imageStorageService.getFileModel(id);
        return processFileModel(fileModel);
    }

    private ResponseEntity<Resource> processFileModel(FileModel fileModel) throws StorageFileNotFoundException {
        var resource = imageStorageService.loadAsResource(fileModel);
        var originalName = fileModel.getOriginalName();
        return ResponseEntity
                .ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + originalName + "\"")
                .body(resource);
    }

    @PostMapping("/")
    @ResponseBody
    public FileModel handleFileUpload(@RequestParam("file") MultipartFile file) throws IOException, NoSuchAlgorithmException {
        return imageStorageService.store(file);
    }
}
