package com.fn.fleischchan.shared;

import com.fn.fleischchan.exceptions.StorageFileInvalidException;
import com.fn.fleischchan.exceptions.StorageFileNotFoundException;
import org.springframework.web.multipart.MultipartFile;

import javax.persistence.*;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.FileAlreadyExistsException;
import java.nio.file.Files;
import java.security.DigestInputStream;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;


/**
 * Database entity connected with an uploaded file.
 */
@Entity
@Table(name = "FILES")
public class FileModel {
    @Id
    @GeneratedValue(generator = "filesSequence")
    @SequenceGenerator(name = "filesSequence", sequenceName = "FILES_SEQ")
    private Integer id;

    /**
     * This is the name via which this file will be referenced.
     */
    @Column(length = 128)
    private String hashOfContents;

    /**
     * This is the name the uploader gave it.
     */
    @Column(length = 128)
    private String originalName;

    public FileModel() {
    }

    public FileModel(StorageScope scope, MultipartFile multipartFile) throws IOException, NoSuchAlgorithmException {
        originalName = multipartFile.getOriginalFilename();
        if (originalName == null)
            throw new StorageFileInvalidException();

        var messageDigest = MessageDigest.getInstance("SHA-256");
        var dataFile = File.createTempFile("fleischchan-", ".tmp");
        dataFile.deleteOnExit();

        try (var fileOutputStream = new FileOutputStream(dataFile);
             var inputStream = multipartFile.getInputStream();
             var digestInputStream = new DigestInputStream(inputStream, messageDigest)) {

            int bytesRead;
            byte[] buffer = new byte[8 * 1024];
            while ((bytesRead = digestInputStream.read(buffer)) != -1)
                fileOutputStream.write(buffer, 0, bytesRead);

            // NOTE: A bit wonky. Copy the temp file to the scope dir, using the hash as a filename.
            hashOfContents = makeHashString(messageDigest, digestInputStream);
        }

        try {
            var trueFile = scope.openFile(hashOfContents);
            Files.move(dataFile.toPath(), trueFile.toPath());
        }

        catch (FileAlreadyExistsException ignored) {
            // Doesn't matter, someone just submitted the same file multiple times.
            // All this means for us is, that we need less storage!
            dataFile.delete();
        }
    }

    private String makeHashString(MessageDigest messageDigest, DigestInputStream digestInputStream) {
        // Make a string of form "<algo-name>$<digest>"
        var base64Digest = Base64
                .getUrlEncoder()
                .encodeToString(digestInputStream.getMessageDigest().digest());

        return String.format("%s$%s", messageDigest.getAlgorithm(), base64Digest);
    }

    public File open(StorageScope scope) throws StorageFileNotFoundException {
        var file = scope.openFile(hashOfContents);
        if (!file.exists())
            throw new StorageFileNotFoundException();

        return file;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getHashOfContents() {
        return hashOfContents;
    }

    public void setHashOfContents(String hashOfContents) {
        this.hashOfContents = hashOfContents;
    }

    public String getOriginalName() {
        return originalName;
    }

    public void setOriginalName(String originalName) {
        this.originalName = originalName;
    }
}
