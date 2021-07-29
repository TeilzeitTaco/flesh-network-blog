package com.fn.fleischchan.exceptions;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

import java.io.IOException;


@ResponseStatus(code = HttpStatus.NOT_FOUND, reason = "file not found")
public class StorageFileNotFoundException extends IOException {
}
