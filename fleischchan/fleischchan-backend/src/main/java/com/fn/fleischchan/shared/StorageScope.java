package com.fn.fleischchan.shared;

import java.io.File;


/**
 * Defines a directory in the "uploaded files" directory.
 */
public enum StorageScope {
    IMAGES_SCOPE("images");

    private final File thisDirectory;

    StorageScope(String path) {
        thisDirectory = new File(getParentDirectory(), path);
        thisDirectory.mkdirs();
    }

    public File openFile(String filename) {
        return new File(thisDirectory, filename);
    }

    private static File getParentDirectory() {
        return new File("storage");
    }
}
