<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"  xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns="http://biotoolsregistry.org" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

    <xsl:param name="mobyle_root" select="mobyle_root"/>

    <xsl:param name="mobyle_contact" select="mobyle_contact"/>

    <xsl:variable name="operations" select="document('mobyle_operations.xml')"/>
    <xsl:variable name="topics" select="document('mobyle_topics.xml')"/>

    <xsl:template match="/program">
        <resources xsi:schemaLocation="http://biotoolsregistry.org/biotools-beta06.xsd" >
        <resource>
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
                <homepage><xsl:value-of select="$mobyle_root" />#forms::<xsl:value-of select="head/name/text()" /></homepage>
                <version><xsl:value-of select="head/version/text()" /></version>
                <collection>Mobyle</collection>
                <xsl:if test="head/package">
                    <collection><xsl:value-of select="head/package/name/text()" />_<xsl:value-of select="head/package/version/text()" /></collection>
                </xsl:if>
                <resourceType uri="http://www.ebi.ac.uk/swo/SWO_0000000">Tool (analysis)</resourceType>
                <interface>
                    <interfaceType>Web UI</interfaceType>
                </interface>
                <description><xsl:value-of select="head/doc/description/text/text()" /></description>
                <xsl:for-each select="$topics//tool[@name=current()/head/name/text()]/topic">
                    <topic uri="{text()}">??</topic>
                </xsl:for-each>
                <function>
                    <xsl:for-each select="$operations//tool[@name=current()/head/name/text()]/operation">
                        <functionName uri="{text()}">??</functionName>
                    </xsl:for-each>
                </function>
                <contact>
                    <contactEmail><xsl:value-of select="$mobyle_contact" /></contactEmail>
                    <contactRole>General</contactRole>
                </contact>
                <!--
                <docs>
                    <xsl:apply-templates select="head/doc/doclink" />
                </docs>
                -->
                <publications>
                    <xsl:apply-templates select="head/doc/reference/@doi" />
                </publications>
                <credits>
                    <xsl:apply-templates select="head/doc/authors" />
                </credits>
                <!--
                <xsl:apply-templates select="head/doc/homepagelink" />
                -->
        </resource>
        </resources>
    </xsl:template>

    <xsl:template match="authors">
        <creditsContributor><xsl:value-of select="text()" /></creditsContributor>
    </xsl:template>

    <xsl:template match="doclink">
        <docsHome><xsl:value-of select="text()" /></docsHome>
    </xsl:template>

    <xsl:template match="homepagelink">
        <homepage><xsl:value-of select="text()" /></homepage>
    </xsl:template>

    <xsl:template match="reference/@doi">
        <publicationsOtherID><xsl:value-of select="." /></publicationsOtherID>
    </xsl:template>

</xsl:stylesheet>
