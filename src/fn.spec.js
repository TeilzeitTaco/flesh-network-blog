describe("Flesh-Network Homepage", () => {
    beforeEach(() => {
        cy.visit("https://flesh-network.ddns.net/")
    })

    it("changes backgrounds", () => {
        cy.get("#background_select").select("Kariert Grau")
        cy.get("body")
            .should("have.css", "background-image")
            .should("not.match", /liniert-korrektur\.jpg/)

        cy.get("#background_select").select("Liniert Korrektur")
        cy.get("body")
            .should("have.css", "background-image")
            .should("match", /liniert-korrektur\.jpg/)
    })

    it("changes font", () => {
        cy.get("#font_select").select("Times New Roman")
        cy.get("body")
            .should("have.css", "font-family")
            .should("not.match", /jmh_typewriter_regular/)

        cy.get("#font_select").select("Typewriter")
        cy.get("body")
            .should("have.css", "font-family")
            .should("match", /jmh_typewriter_regular/)
    })
})
