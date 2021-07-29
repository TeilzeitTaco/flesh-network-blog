package com.fn.fleischchan.letters;

import com.fn.fleischchan.shared.FileModel;
import org.hibernate.annotations.CreationTimestamp;

import javax.persistence.*;
import java.util.Date;


@Entity
@Table(name = "LETTERS")
public class Letter {
    @Id
    @GeneratedValue(generator = "lettersSequence")
    @SequenceGenerator(name = "lettersSequence", sequenceName = "LETTERS_SEQ")
    private Integer id;

    @Column(length = 128)
    private String title, author;

    @Column(length = 8192)
    private String content;

    @CreationTimestamp()
    @GeneratedValue(strategy=GenerationType.IDENTITY)
    @Temporal(TemporalType.TIMESTAMP)
    private Date timestamp;

    @OneToOne(cascade = CascadeType.ALL, fetch = FetchType.EAGER)
    private FileModel attachedImage;

    public Date getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(Date timestamp) {
        this.timestamp = timestamp;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public String getAuthor() {
        return author;
    }

    public void setAuthor(String author) {
        this.author = author;
    }

    public Integer getId() {
        return id;
    }

    public FileModel getAttachedImage() {
        return attachedImage;
    }

    public void setAttachedImage(FileModel attachedImage) {
        this.attachedImage = attachedImage;
    }

    public boolean hasAttachedImage() {
        return this.attachedImage != null;
    }
}
