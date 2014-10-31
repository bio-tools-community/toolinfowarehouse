<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"  xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns="http://biotoolsregistry.org" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

    <xsl:variable name="operations" select="document('mobyle_operations.xml')"/>
    <xsl:variable name="topics" select="document('mobyle_topics.xml')"/>

    <xsl:template match="/program">
        <tools xsi:schemaLocation="http://biotoolsregistry.org/biotools-beta04.xsd" >
        <tool>
                <name>
                    <xsl:text>Mobyle_</xsl:text>
                    <xsl:if test="head/package/name">
                        <xsl:value-of select="head/package/name/text()" />
                        <xsl:text>_</xsl:text>
                        <xsl:value-of select="head/package/version/text()" />
                        <xsl:text>_</xsl:text>
                    </xsl:if>
                    <xsl:value-of select="head/name/text()" />
                    <xsl:if test="head/version">
                        <xsl:text>_</xsl:text>
                        <xsl:value-of select="head/version/text()" />
                    </xsl:if>
                </name>
                <version><xsl:value-of select="head/version/text()" /></version>
                <collectionName>Mobyle</collectionName>
                <xsl:if test="head/package">
                    <collectionName><xsl:value-of select="head/package/name/text()" />_<xsl:value-of select="head/package/version/text()" /></collectionName>
                </xsl:if>
                <softwareType uri="http://www.ebi.ac.uk/swo/SWO_0000000">Web UI</softwareType>
                <description><xsl:value-of select="head/description/text/text()" /></description>
                <xsl:apply-templates select="head/doc/authors" />
                <xsl:apply-templates select="head/doc/doclink" />
                <xsl:apply-templates select="head/doc/homepagelink" />
                <publications>
                    <xsl:apply-templates select="head/doc/reference/@doi" />
                </publications>
                <function>
                    <xsl:for-each select="$operations//tool[@name=current()/head/name/text()]/operation">
                        <functionName uri="{text()}">??</functionName>
                    </xsl:for-each>
                </function>
                <xsl:for-each select="$topics//tool[@name=current()/head/name/text()]/topic">
                    <topic uri="{text()}">??</topic>
                </xsl:for-each>
        </tool>
        </tools>
    </xsl:template>

    <xsl:template match="authors">
        <credits>
                <contributor><xsl:value-of select="text()" /></contributor>
        </credits>
    </xsl:template>

    <xsl:template match="doclink">
        <docs>
            <docsHome><xsl:value-of select="text()" /></docsHome>
        </docs>
    </xsl:template>

    <xsl:template match="homepagelink">
        <homepage><xsl:value-of select="text()" /></homepage>
    </xsl:template>

    <xsl:template match="reference/@doi">
        <publicationOtherID><xsl:value-of select="." /></publicationOtherID>
    </xsl:template>

</xsl:stylesheet>
