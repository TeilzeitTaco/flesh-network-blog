package com.fn.fleischchan.shared;

import com.fn.fleischchan.exceptions.StorageFileNotFoundException;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.security.NoSuchAlgorithmException;


@Service
public class ImageStorageService {
    private final FileRepository fileRepository;

    public ImageStorageService(FileRepository fileRepository) {
        this.fileRepository = fileRepository;
    }

    public FileModel store(MultipartFile uploadedFile) throws IOException, NoSuchAlgorithmException {
        var fileModel = new FileModel(StorageScope.IMAGES_SCOPE, uploadedFile);
        fileRepository.save(fileModel);
        return fileModel;
    }

    public Resource loadAsResource(FileModel fileModel) throws StorageFileNotFoundException {
        var accessedFile = fileModel.open(StorageScope.IMAGES_SCOPE);
        return new FileSystemResource(accessedFile);
    }

    public FileModel getFileModel(Integer id) {
        return fileRepository.findById(id).orElse(null);
    }

    public FileModel getFileModel(String hashOfContents) {
        return fileRepository.findFirstByHashOfContents(hashOfContents).orElse(null);
    }
}
