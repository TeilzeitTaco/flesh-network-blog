package com.fn.fleischchan.exceptions;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

import java.io.IOException;


@ResponseStatus(code = HttpStatus.BAD_REQUEST, reason = "invalid format")
public class StorageFileInvalidException extends IOException {
}
