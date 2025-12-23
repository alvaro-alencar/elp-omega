plugins {
    kotlin("jvm") version "1.9.21"
    `maven-publish`
}

group = "dev.vortex"
version = "1.0.0"

repositories {
    mavenCentral()
}

dependencies {
    implementation(kotlin("stdlib"))
    implementation("org.slf4j:slf4j-api:2.0.9")
    
    testImplementation(kotlin("test"))
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.1")
    testImplementation("io.mockk:mockk:1.13.8")
    testImplementation("org.slf4j:slf4j-simple:2.0.9")
}

tasks.test {
    useJUnitPlatform()
}

kotlin {
    jvmToolchain(17)
}

publishing {
    publications {
        create<MavenPublication>("maven") {
            from(components["java"])
            
            pom {
                name.set("ELP-Omega Kotlin")
                description.set("Entangled Logic Protocol - Kotlin/JVM Implementation")
                url.set("https://github.com/yourusername/elp-omega")
                
                licenses {
                    license {
                        name.set("MIT License")
                        url.set("https://opensource.org/licenses/MIT")
                    }
                }
                
                developers {
                    developer {
                        id.set("alvaro-alencar")
                        name.set("Álvaro Alencar")
                        email.set("alvaro@vortex.dev")
                    }
                }
            }
        }
    }
}