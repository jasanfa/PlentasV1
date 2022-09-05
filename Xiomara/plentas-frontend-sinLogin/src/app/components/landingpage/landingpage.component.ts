import { Component } from "@angular/core";

@Component({
    selector: 'landingpage',
    templateUrl: './landingpage.component.html',
    styleUrls: ['./landingpage.component.css'], 
})

export class LandingPageClass{
    constructor(){
        console.log("Componente cargado")
    }
}