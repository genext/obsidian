---
title: "record"
created: 2025-08-20 10:46:32
updated: 2025-09-16 08:48:15
---
  * better than defining VO, DTO except special use cases
    * mutable fields
    * inheritance hierarchies
    * differencey in field visibility
  * a compact way to create **immutable** data carrier class.
  * automatically generates common methods like equals, hashCode, toString, and getter
  * sample code
    * String 타입 input 속성을 가진 TextInput 클래스 생성
      * ```java
public record TextInput(String input) {
}```
      * 위 코드는 실질적으로 다음과 같다.
        * ```java
public class TextInput {
    private final String input;
    
    public TextInput(String input) {
        this.input = input;
    }
    
    public String input() {  // Note: getter method name matches field name
        return input;
    }
    
    @Override
    public boolean equals(Object obj) {
        // Auto-generated implementation
    }
    
    @Override
    public int hashCode() {
        // Auto-generated implementation
    }
    
    @Override
    public String toString() {
        // Auto-generated implementation like "TextInput[input=hello]"
    }
}```
    * record와 pojo 비교
      * java 17+, record
        * ```java
@ConfigurationProperties("app")
@Validated  
public record AppProperties(
    @NotNull @Positive Integer bufferMaxSize,
    @NotBlank String collectionName,
    @Valid EnrichingProperties enriching
) { }```
      * java 16, pojo
        * ```java
@ConfigurationProperties("app")
@Validated
public class AppProperties {
    
    @NotNull
    @Positive
    private Integer bufferMaxSize;
    
    @NotBlank
    private String collectionName;
    
    @Valid
    private EnrichingProperties enriching;
    
    // Default constructor --> record는 canonical constructor만
    public AppProperties() {
    }
    
    // Constructor with all parameters
    public AppProperties(Integer bufferMaxSize, String collectionName, EnrichingProperties enriching) {
        this.bufferMaxSize = bufferMaxSize;
        this.collectionName = collectionName;
        this.enriching = enriching;
    }
    
    // Getters
    public Integer getBufferMaxSize() {
        return bufferMaxSize;
    }
    
    public String getCollectionName() {
        return collectionName;
    }
    
    public EnrichingProperties getEnriching() {
        return enriching;
    }
    
    // Setters  --> record는 immutable이기 때문에 삭제.
    public void setBufferMaxSize(Integer bufferMaxSize) {
        this.bufferMaxSize = bufferMaxSize;
    }
    
    public void setCollectionName(String collectionName) {
        this.collectionName = collectionName;
    }
    
    public void setEnriching(EnrichingProperties enriching) {
        this.enriching = enriching;
    }
    
    // equals() method
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        
        AppProperties that = (AppProperties) o;
        
        if (!Objects.equals(bufferMaxSize, that.bufferMaxSize)) return false;
        if (!Objects.equals(collectionName, that.collectionName)) return false;
        return Objects.equals(enriching, that.enriching);
    }
    
    // hashCode() method
    @Override
    public int hashCode() {
        return Objects.hash(bufferMaxSize, collectionName, enriching);
    }
    
    // toString() method
    @Override
    public String toString() {
        return "AppProperties{" +
                "bufferMaxSize=" + bufferMaxSize +
                ", collectionName='" + collectionName + '\'' +
                ", enriching=" + enriching +
                '}';
    }
}```
    * 복잡한 예.
      * ```java
@JsonIgnoreProperties(ignoreUnknown = true)
    public record Alert(@JsonProperty("features") List<Feature> features) {

        @JsonIgnoreProperties(ignoreUnknown = true)
        public record Feature(@JsonProperty("properties") Properties properties) {
        }

        @JsonIgnoreProperties(ignoreUnknown = true)
        public record Properties(@JsonProperty("event") String event, @JsonProperty("areaDesc") String areaDesc,
                @JsonProperty("severity") String severity, @JsonProperty("description") String description,
                @JsonProperty("instruction") String instruction) {
        }
    }
}```
      * 위 코드는 다음과 같다.
        * Inner class가 static임에 유의!
        * ```java
import java.util.List;
import java.util.Objects;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public class Alert {
    
    @JsonProperty("features")
    private List<Feature> features;
    
    // Default constructor (required for Jackson)
    public Alert() {
    }
    
    // Constructor with parameters
    public Alert(List<Feature> features) {
        this.features = features;
    }
    
    // Getter
    public List<Feature> getFeatures() {
        return features;
    }
    
    // Setter
    public void setFeatures(List<Feature> features) {
        this.features = features;
    }
    
    // equals method
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Alert alert = (Alert) obj;
        return Objects.equals(features, alert.features);
    }
    
    // hashCode method
    @Override
    public int hashCode() {
        return Objects.hash(features);
    }
    
    // toString method
    @Override
    public String toString() {
        return "Alert{" +
                "features=" + features +
                '}';
    }
    
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Feature {
        
        @JsonProperty("properties")
        private Properties properties;
        
        // Default constructor
        public Feature() {
        }
        
        // Constructor with parameters
        public Feature(Properties properties) {
            this.properties = properties;
        }
        
        // Getter
        public Properties getProperties() {
            return properties;
        }
        
        // Setter
        public void setProperties(Properties properties) {
            this.properties = properties;
        }
        
        // equals method
        @Override
        public boolean equals(Object obj) {
            if (this == obj) return true;
            if (obj == null || getClass() != obj.getClass()) return false;
            Feature feature = (Feature) obj;
            return Objects.equals(properties, feature.properties);
        }
        
        // hashCode method
        @Override
        public int hashCode() {
            return Objects.hash(properties);
        }
        
        // toString method
        @Override
        public String toString() {
            return "Feature{" +
                    "properties=" + properties +
                    '}';
        }
    }
    
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Properties {
        
        @JsonProperty("event")
        private String event;
        
        @JsonProperty("areaDesc")
        private String areaDesc;
        
        @JsonProperty("severity")
        private String severity;
        
        @JsonProperty("description")
        private String description;
        
        @JsonProperty("instruction")
        private String instruction;
        
        // Default constructor
        public Properties() {
        }
        
        // Constructor with all parameters
        public Properties(String event, String areaDesc, String severity, 
                         String description, String instruction) {
            this.event = event;
            this.areaDesc = areaDesc;
            this.severity = severity;
            this.description = description;
            this.instruction = instruction;
        }
        
        // Getters
        public String getEvent() {
            return event;
        }
        
        public String getAreaDesc() {
            return areaDesc;
        }
        
        public String getSeverity() {
            return severity;
        }
        
        public String getDescription() {
            return description;
        }
        
        public String getInstruction() {
            return instruction;
        }
        
        // Setters
        public void setEvent(String event) {
            this.event = event;
        }
        
        public void setAreaDesc(String areaDesc) {
            this.areaDesc = areaDesc;
        }
        
        public void setSeverity(String severity) {
            this.severity = severity;
        }
        
        public void setDescription(String description) {
            this.description = description;
        }
        
        public void setInstruction(String instruction) {
            this.instruction = instruction;
        }
        
        // equals method
        @Override
        public boolean equals(Object obj) {
            if (this == obj) return true;
            if (obj == null || getClass() != obj.getClass()) return false;
            Properties that = (Properties) obj;
            return Objects.equals(event, that.event) &&
                   Objects.equals(areaDesc, that.areaDesc) &&
                   Objects.equals(severity, that.severity) &&
                   Objects.equals(description, that.description) &&
                   Objects.equals(instruction, that.instruction);
        }
        
        // hashCode method
        @Override
        public int hashCode() {
            return Objects.hash(event, areaDesc, severity, description, instruction);
        }
        
        // toString method
        @Override
        public String toString() {
            return "Properties{" +
                    "event='" + event + '\'' +
                    ", areaDesc='" + areaDesc + '\'' +
                    ", severity='" + severity + '\'' +
                    ", description='" + description + '\'' +
                    ", instruction='" + instruction + '\'' +
                    '}';
        }
    }
}```
  * AI research
    * 요약
      * # Real-World Java Records in REST APIs
        * records excel for specific REST API use cases while facing significant limitations that prevent universal adoption.
        * Records deliver measurable performance benefits with 10% faster field access operations blogspot and equivalent JSON serialization performance
      * ## Industry adoption shows selective but growing usage
        * records are commonly used in Spring Boot 3.0+ applications for specific scenarios.
        * Popular open source projects like Spring Boot samples and microservice architectures increasingly use records for configuration properties (@ConfigurationProperties), request objects (@RequestBody), and API responses.
        * Enterprise Java 17 adoption has reached 35% (New Relic 2024), creating the foundation for records usage in production environments.
      * ## GitHub repositories reveal specific implementation patterns: four dominant usage patterns for records in REST APIs.
        * **Configuration properties** represent the most successful adoption area. Spring Boot applications routinely replace traditional @ConfigurationProperties classes with records
          * ```javascript
@ConfigurationProperties("app")
@Validated  
public record AppProperties(
    @NotNull @Positive Integer bufferMaxSize,
    @NotBlank String collectionName,
    @Valid EnrichingProperties enriching
) { }```
        * **Request DTOs** with validation work seamlessly when using `@Valid` instead of `@Validated` for nested objects:
          * ```javascript
public record CreateUserRequest(
    @NotBlank @Size(max = 50) String username,
    @Email String email,
    @Min(18) int age
) { }```
        * **API response objects** leverage records' immutability for thread-safe data transfer:
          * ```java
public record UserResponse(Long id, String name, String email) { }

@GetMapping("/users/{id}")
public UserResponse getUser(@PathVariable Long id) {
    return userService.findById(id);
}```
        * **Complex nested structures** use records with Jackson annotations, though requiring explicit `@JsonProperty` annotations: [github](https://github.com/refactorizando-web/java-record)
          * ```java
public record MovieResponse(
    @JsonProperty("id") String id,
    @JsonProperty("director") DirectorRecord director,
    @JsonProperty("released") Boolean released
) { }```
      * ## Performance benchmarks favor records with caveats
        * **records outperform traditional classes by approximately 10%** for field access operations.
        * **JSON serialization performance shows equivalent results** between records and POJOs when using Jackson 2.12+, same performance
        * However, serialization bottlenecks typically dominate REST API performance profiles, making the records advantage less significant in practice.
      * The lack of inheritance support creates challenges for polymorphic API designs.
      * records for data transfer, traditional classes for complex business logic.
      * version requirements and limitations. 
        * Jackson 2.12+ provides comprehensive record serialization support, [Youribonnaffe](https://youribonnaffe.github.io/java/records/spring/2021/01/10/records-spring-boot.html) requiring only explicit `@JsonProperty` annotations for JSON mapping. [Restack](https://www.restack.io/p/json-utilities-knowledge-jackson-json-performance-answer-cat-ai)
      * **Bean validation works well with caveats**. 
        * Standard annotations (`@NotNull`, `@Size`, `@Email`) apply correctly to record components, [GitHub](https://gist.github.com/aoudiamoncef/5e0562d3f4a25965eccbddb2b573f91d) but nested validation requires `@Valid` rather than `@Validated`.
      * **Spring Data JPA creates the most significant limitation**.
        * Records cannot serve as JPA entities due to immutability requirements and lack of no-argument constructors.
        * However, records excel for query projections and DTO mappings: [🔗](https://youribonnaffe.github.io/java/records/spring/2021/01/10/records-spring-boot.html)
          * ```java
@Query("SELECT new com.example.UserSummary(u.name, u.email) FROM User u")
List<UserSummary> findAllSummaries();

public record UserSummary(String name, String email) {}```
      * Records require Jackson 2.12+, Spring Boot 2.6+, and Java 16+ minimum versions.
    * Real-World Java Records in REST APIs
      * roam markdown version
        * # Real-World Java Records in REST APIs
          * Java records have achieved **55% adoption among developers** according to 2024 surveys, establishing them as the most popular new Java feature. Yet enterprise production usage reveals a more nuanced story: records excel for specific REST API use cases while facing significant limitations that prevent universal adoption.
          * Records deliver **measurable performance benefits** with 10% faster field access operations and equivalent JSON serialization performance, making them technically superior to traditional POJOs for data transfer objects. The immutability guarantee and dramatic boilerplate reduction have won over developers, but architectural constraints around inheritance and JPA compatibility create clear boundaries for their use.
        * ## Industry adoption shows selective but growing usage
          * Current adoption patterns reveal records are **commonly used in Spring Boot 3.0+ applications** for specific scenarios. The BellSoft 2024 Java Developer Survey found records leading as the most adopted new feature at 55%, significantly ahead of pattern matching (53%) and other language enhancements. However, this enthusiasm masks enterprise caution - only 37% of organizations use even one new Java feature in production.
          * **Real production codebases** demonstrate clear patterns. Spring's official REST service guides now showcase records as the standard approach for DTOs. Popular open source projects like Spring Boot samples and microservice architectures increasingly use records for configuration properties (`@ConfigurationProperties`), request objects (`@RequestBody`), and API responses.
          * The adoption timeline shows acceleration since Java 17's LTS status in September 2021. Enterprise Java 17 adoption has reached 35% (New Relic 2024), creating the foundation for records usage in production environments. Java 21 adoption at 30% in its first year signals even faster enterprise modernization, suggesting records adoption will accelerate.
        * ## GitHub repositories reveal specific implementation patterns
          * Analysis of real codebases shows **four dominant usage patterns** for records in REST APIs:
          * **Configuration properties** represent the most successful adoption area. Spring Boot applications routinely replace traditional `@ConfigurationProperties` classes with records:
          * ```java
@ConfigurationProperties("app")
@Validated  
public record AppProperties(
    @NotNull @Positive Integer bufferMaxSize,
    @NotBlank String collectionName,
    @Valid EnrichingProperties enriching
) { }```
          * **Request DTOs** with validation work seamlessly when using `@Valid` instead of `@Validated` for nested objects:
          * ```java
public record CreateUserRequest(
    @NotBlank @Size(max = 50) String username,
    @Email String email,
    @Min(18) int age
) { }```
          * **API response objects** leverage records' immutability for thread-safe data transfer:
          * ```java
public record UserResponse(Long id, String name, String email) { }

@GetMapping("/users/{id}")
public UserResponse getUser(@PathVariable Long id) {
    return userService.findById(id);
}```
          * **Complex nested structures** use records with Jackson annotations, though requiring explicit `@JsonProperty` annotations:
          * ```java
public record MovieResponse(
    @JsonProperty("id") String id,
    @JsonProperty("director") DirectorRecord director,
    @JsonProperty("released") Boolean released
) { }```
          * GitHub repository analysis reveals that **migration from traditional classes to records** typically occurs during Spring Boot 3.0 upgrades, when projects gain Java 17+ baseline requirements and improved framework support.
        * ## Performance benchmarks favor records with caveats
          * Comprehensive JMH benchmarking demonstrates **records outperform traditional classes by approximately 10%** for field access operations. Specific benchmark results show records at 9.412 ± 0.181 ns/op versus regular classes at 10.424 ± 0.257 ns/op, attributable to HotSpot VM optimizations that mark records as "trusted" for constant folding.
          * **JSON serialization performance shows equivalent results** between records and POJOs when using Jackson 2.12+. Independent benchmarking from fabienrenaud's java-json-benchmark project confirms ~703,692 operations per second for Jackson with records, matching POJO performance. This eliminates concerns about REST API response times when switching to records.
          * **Memory usage patterns favor records slightly** due to better escape analysis from immutability guarantees, though object allocation rates remain equivalent. GraalVM native image compilation shows identical performance characteristics, with no startup time differences or memory footprint changes.
          * The performance story becomes compelling for **high-throughput REST APIs** where the 10% field access improvement accumulates across millions of operations. However, serialization bottlenecks typically dominate REST API performance profiles, making the records advantage less significant in practice.
        * ## Developer community embraces records with clear boundaries
          * Community sentiment analysis across Stack Overflow, Reddit r/java, and Spring forums reveals **overwhelmingly positive reception tempered by practical constraints**. Developers consistently praise records for eliminating boilerplate code and providing immutability guarantees, with 80% satisfaction rates for appropriate use cases.
          * **Success stories cluster around specific scenarios**: REST DTOs, configuration classes, and value objects with simple validation requirements. Conference presentations and technical blogs emphasize records as solving long-standing Java verbosity problems while maintaining type safety.
          * **Community concerns focus on architectural limitations** rather than technical issues. The inability to use records as JPA entities represents the most frequently cited limitation, forcing developers to maintain separate entity and DTO classes. The lack of inheritance support creates challenges for polymorphic API designs.
          * Developer testimonials reveal **mature understanding of appropriate use cases**. The community has moved beyond initial enthusiasm to nuanced adoption patterns: records for data transfer, traditional classes for complex business logic. This pragmatic approach indicates healthy ecosystem evolution.
        * ## Framework compatibility creates mixed experiences
          * Spring Boot ecosystem integration shows **good to excellent support** across most tools, though with version requirements and limitations. Jackson 2.12+ provides comprehensive record serialization support, requiring only explicit `@JsonProperty` annotations for JSON mapping.
          * **Bean validation works well with caveats**. Standard annotations (`@NotNull`, `@Size`, `@Email`) apply correctly to record components, but nested validation requires `@Valid` rather than `@Validated`. Complex validation scenarios may need traditional classes for full functionality.
          * **Spring Data JPA creates the most significant limitation**. Records cannot serve as JPA entities due to immutability requirements and lack of no-argument constructors. However, records excel for query projections and DTO mappings:
          * ```java
@Query("SELECT new com.example.UserSummary(u.name, u.email) FROM User u")
List<UserSummary> findAllSummaries();

public record UserSummary(String name, String email) {}```
          * **OpenAPI/Swagger documentation generation remains problematic**. The OpenAPI Generator lacks native record support (GitHub issue #10490 still open), requiring workarounds like custom Mustache templates or alternative tools like openapi-processor-spring.
          * Testing frameworks show **excellent compatibility** with no special configuration required. MockMvc, TestContainers, and Spring Boot Test work seamlessly with record-based DTOs and request objects.
        * ## Concrete limitations drive pragmatic adoption
          * Real-world usage reveals **seven key constraints** that prevent universal records adoption for REST parameters:
          * **JPA entity incompatibility** ranks as the primary limitation. Hibernate and other ORM frameworks require mutable entities with no-argument constructors, forcing developers to maintain separate entity and DTO classes. Jakarta Persistence 3.2 will support records as embeddable types, but full entity support remains unlikely.
          * **Inheritance restrictions** prevent polymorphic API designs. Records cannot extend classes or be extended, limiting their use in hierarchical data structures. API endpoints requiring subtype relationships must use traditional class hierarchies.
          * **Limited customization options** constrain complex scenarios. Records cannot override generated methods like `toString()` or add instance fields beyond components. This inflexibility affects APIs requiring custom serialization logic or computed properties.
          * **Jackson annotation requirements** create migration overhead. Unlike POJOs that work with default Jackson settings, records need explicit `@JsonProperty` annotations for proper JSON field mapping. This affects existing APIs where field names must remain consistent.
          * **Validation complexity** forces some scenarios back to traditional classes. Cross-field validation, conditional constraints, and custom validation groups work better with mutable classes that support full Bean Validation features.
          * **Framework version dependencies** create adoption barriers. Records require Jackson 2.12+, Spring Boot 2.6+, and Java 16+ minimum versions. Enterprise environments with older framework versions cannot adopt records without significant upgrades.
          * **OpenAPI toolchain gaps** affect API-first development. The lack of comprehensive OpenAPI generator support creates friction for teams using code generation workflows, requiring tool changes or manual workarounds.
        * ## Trends indicate accelerating enterprise adoption
          * Enterprise adoption patterns suggest **records usage will accelerate through 2025** as Java 17/21 becomes the new enterprise baseline. The correlation between Java version upgrades and records adoption indicates that enterprise modernization cycles drive feature uptake more than individual developer preferences.
          * **Training and education content has matured** from basic tutorials to advanced integration patterns, reducing adoption barriers. Major Java conferences consistently feature records content, with focus shifting from introductory material to enterprise case studies and best practices.
          * **Framework ecosystem support continues improving**. Spring Boot 3's full records support, Jakarta EE 11 specifications, and improved tooling create favorable conditions for broader enterprise adoption. The resolution of early Jackson compatibility issues has eliminated technical roadblocks.
          * **Cloud-native and greenfield projects show highest adoption rates**, suggesting records work best when architectural constraints don't require backward compatibility. Organizations with active Java upgrade cycles and modern development practices lead records adoption.
          * The evidence strongly suggests **selective but growing records usage** in enterprise REST APIs, with clear patterns emerging for appropriate use cases and architectural boundaries.
      * raw markdown
        * ![[100. media/other/_L9Zzoq7sG.md]]
      * pdf version
        * ![[100. media/documents/zGxx8vClIp.pdf]]