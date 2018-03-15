"""

The purposes of this code are:
	1. to test different ways of handling the dependency issue described in https://bugzilla.ipr.univ-rennes1.fr/show_bug.cgi?id=2158 :
		Specifically, it provides solutions for handling library dependencies : game1 uses gameengine library, which requires some headers from math library : what we want is that mymath headers are found even if game1 doesn't know anything about mymath library (it needs it indirectly through gameengine library)
	2. to provide templates for best usage of cmake system
		This template is based on https://pabloariasal.github.io/2018/02/19/its-time-to-do-cmake-right/
		In the future, the code might be turned into a useful helper tool to generate cmake files, at least for simple projects (as cmake does have a learning curve that is often outside the scope of some developers; writing simple cmake is easy, writing proper cmake is not that easy)
"""

import os
import os.path
from enum import Enum
from subprocess import call
import shutil


class SourceSet(object):
	"""
	a group of source code projects (in which a project that may or may not be dependent on another project)
	
	This is the equivalent of what microsft visual studio calls a "solution"
	"""

	def __init__(self):
		self.projects = {}

	def add_project(self, project):
		self.projects[project.name] = project


class ProjectType(Enum):
	static_library = 1
	application = 2
	

class Project(object):
	"""
	a source code project that contains all the necessary stuff to build a binary (whether it's a library or an executable)
	"""
	def __init__(self, project_name, project_type):
		self.name = project_name
		self.type = project_type
		self.source_files = {}
		self.dependencies = {}
		
	def add_source(self, source_file):
		self.source_files[source_file.name] = source_file
		
	def has_cpp_files(self):
		for source_file in self.source_files.values():
			if not source_file.is_header():
				return True
		return False
		
	def add_dependency(self, dep_project):
		self.dependencies[dep_project.name] = dep_project	

	
class SourceFile(object):
	"""
	represents a source code file
	"""

	def __init__(self, file_name, file_contents = None):
		self.name = file_name
		self.content = file_contents

	def is_header(self):
		if self.name.split('.')[-1] in ['hpp', 'hxx', 'h']:
			return True
		else:
			return False

class ISourceSetExporter(object):
	def export_source_set(self, source_set):
		pass

def myopen(file_path, mode):
	os.makedirs(os.path.dirname(file_path), exist_ok=True)
	return open(file_path, mode)


class CMakeExporter(ISourceSetExporter):
	"""
	an source set exporter that generates build instructions based on cmake
	"""
	class DepHandlingMethod(Enum):
		use_master = 1 # method described in https://cmake.org/pipermail/cmake/2010-March/035848.html
		use_subdir = 2

	def __init__(self, export_path, dep_handling_method):
		self.export_path = export_path
		self.dep_handling_method = dep_handling_method

	def export_source_file(self, source_file, project_root_path, project):
		if source_file.is_header():
			relative_path = 'include/' + project.name
		else:
			relative_path = 'src'
		source_file_path = project_root_path + '/' + relative_path + '/' + source_file.name
		with myopen(source_file_path, 'w') as f:
			f.write(source_file.content)

	def get_project_root_path(self, project):
		return self.export_path + '/' + {ProjectType.static_library:'lib', ProjectType.application:'app'}[project.type] + '/' + project.name


	def export_project_config_in(self, project):
		project_root_path = self.get_project_root_path(project)
		with myopen(project_root_path+'/cmake/'+project.name+'config.cmake.in', 'w') as f:
			f.write('get_filename_component('+project.name+'_CMAKE_DIR "${CMAKE_CURRENT_LIST_FILE}" PATH)\n')
			f.write('include(CMakeFindDependencyMacro)\n')
			
			f.write('list(APPEND CMAKE_MODULE_PATH ${'+project.name+'_CMAKE_DIR})\n')

			# NOTE Had to use find_package because find_dependency does not support COMPONENTS or MODULE until 3.8.0
			for dep_project in project.dependencies.values():
				f.write('find_package('+dep_project.name+' 1.0 REQUIRED)\n')
			#find_dependency(Boost 1.55 REQUIRED COMPONENTS regex)
			#find_dependency(RapidJSON 1.0 REQUIRED MODULE)
			#find_package(Boost 1.55 REQUIRED COMPONENTS regex)
			#find_package(RapidJSON 1.0 REQUIRED MODULE)
			
			f.write('list(REMOVE_AT CMAKE_MODULE_PATH -1)\n')

			# if(NOT TARGET math::math)
			# 	include("${math_CMAKE_DIR}/MathTargets.cmake")
			# endif()
			f.write('if(NOT TARGET %s::%s)\n' % (project.name, project.name))
			f.write('	include("${%s_CMAKE_DIR}/%sTargets.cmake")\n' % (project.name, project.name))
			f.write('endif()\n')
			
			# set(math_LIBRARIES math::math)
			f.write('set(%s_LIBRARIES %s::%s)\n' % (project.name, project.name, project.name))


	def export_project(self, project):
		project_root_path = self.get_project_root_path(project)
		try:
			shutil.rmtree(project_root_path)
		except:
			pass
		
		for source_file in project.source_files.values():
			self.export_source_file(source_file, project_root_path, project)
		# create the CMakeLists.txt
		with myopen(project_root_path+'/CMakeLists.txt', 'w') as f:
			f.write('cmake_minimum_required(VERSION 3.5)\n')
			cmake_project_name = {ProjectType.static_library:'lib', ProjectType.application:'app'}[project.type] + project.name
			f.write('project('+cmake_project_name+' VERSION 1.0.0 LANGUAGES CXX)\n')
			
			target_create_command = {ProjectType.static_library:'add_library', ProjectType.application:'add_executable'}[project.type]
			f.write(target_create_command+'('+project.name+' ')
			
			for source_file in project.source_files.values():
				if not source_file.is_header():
					f.write('src/'+source_file.name+' ')
			if not project.has_cpp_files():
				f.write('INTERFACE')
			f.write(')\n')
			
			for dep_project in project.dependencies.values():
				if self.dep_handling_method == CMakeExporter.DepHandlingMethod.use_master:
					f.write('find_package('+dep_project.name+' 1.0 REQUIRED)\n')
				elif self.dep_handling_method == CMakeExporter.DepHandlingMethod.use_subdir:
					dep_project_build_relative_path = dep_project.name
					f.write('add_subdirectory("%s" "%s")\n' % (self.get_project_root_path(dep_project), dep_project_build_relative_path) )
					f.write('add_dependencies(%s %s)\n' % (project.name, dep_project.name))
			
			f.write('target_include_directories('+project.name+'\n')
			if project.has_cpp_files():
				f.write('  PUBLIC\n')
			else:
				f.write('  INTERFACE\n')
			f.write('    $<INSTALL_INTERFACE:include>\n')
			f.write('    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>\n')
			f.write(')\n')

			f.write('target_link_libraries('+project.name+'\n')
			f.write('  PUBLIC\n')
			for dep_project in project.dependencies.values():
				if self.dep_handling_method == CMakeExporter.DepHandlingMethod.use_master:
					f.write('    '+dep_project.name+'::'+dep_project.name+'\n')
				elif self.dep_handling_method == CMakeExporter.DepHandlingMethod.use_subdir:
					f.write('    '+dep_project.name+'\n')
			f.write(')\n')
				
			if project.has_cpp_files():
				f.write('target_compile_options(gameengine PRIVATE -Werror)\n')
				f.write('target_compile_features(gameengine PRIVATE cxx_std_11)\n')
			# 				
			f.write('##############################################\n')
			f.write('# Installation instructions\n')
			f.write('\n')
			f.write('include(GNUInstallDirs)\n')
			f.write('set(INSTALL_CONFIGDIR ${CMAKE_INSTALL_LIBDIR}/cmake/%s)\n' % project.name)
			f.write('\n')
			f.write('install(TARGETS %s\n' % project.name)
			f.write('   EXPORT %s-targets\n' % project.name)
			f.write('	LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}\n')
			f.write('   ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}\n')
			f.write(')\n')
			f.write('\n')
			f.write('install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})\n')
			f.write('\n')
			f.write('# This would be required if we wanted the exported target to have a different name than math (eg MyMath)\n')
			f.write('#set_target_properties(math PROPERTIES EXPORT_NAME MyMath)\n')
			f.write('\n')
			
			f.write('# Export the targets to a script\n')
			f.write('install(EXPORT %s-targets\n' % project.name)
			f.write('  FILE\n')
			f.write('    %sTargets.cmake\n' % project.name)
			f.write('  NAMESPACE\n')
			f.write('    %s::\n' % project.name)
			f.write('  DESTINATION\n')
			f.write('    ${INSTALL_CONFIGDIR}\n')
			f.write(')\n')
			f.write('\n')
			
			f.write('# Create a ConfigVersion.cmake file\n')
			f.write('include(CMakePackageConfigHelpers)\n')
			f.write('write_basic_package_version_file(\n')
			f.write('    ${CMAKE_CURRENT_BINARY_DIR}/%sConfigVersion.cmake\n' % project.name)
			f.write('    VERSION ${PROJECT_VERSION}\n')
			f.write('    COMPATIBILITY AnyNewerVersion\n')
			f.write(')\n')

			f.write('\n')
			
			f.write('configure_package_config_file(${CMAKE_CURRENT_LIST_DIR}/cmake/%sConfig.cmake.in\n' % project.name)
			f.write('    ${CMAKE_CURRENT_BINARY_DIR}/%sConfig.cmake\n' % project.name)
			f.write('    INSTALL_DESTINATION ${INSTALL_CONFIGDIR}\n')
			f.write(')\n')

			f.write('\n')

			f.write('# Install the config, configversion and custom find modules\n')
			f.write('install(FILES\n')
			f.write('    ${CMAKE_CURRENT_BINARY_DIR}/%sConfig.cmake\n' % project.name)
			f.write('    ${CMAKE_CURRENT_BINARY_DIR}/%sConfigVersion.cmake\n' % project.name)
			f.write('    DESTINATION ${INSTALL_CONFIGDIR}\n')
			f.write(')\n')
			
			f.write('\n')
			
			f.write('##############################################\n')
			f.write('## Exporting from the build tree\n')
			f.write('\n')
			f.write('export(EXPORT %s-targets FILE ${CMAKE_CURRENT_BINARY_DIR}/%sTargets.cmake NAMESPACE %s::)\n' % (project.name, project.name, project.name))
			f.write('\n')
			f.write('#Register package in user s package registry\n')
			f.write('export(PACKAGE %s)\n' % project.name)
				
		self.export_project_config_in(project)
		
		if self.dep_handling_method == CMakeExporter.DepHandlingMethod.use_master:
			master_cmake_path = '%s/cmake/master/CMakeLists.txt' % project_root_path
			with myopen(master_cmake_path, 'w') as f:
				f.write('cmake_minimum_required(VERSION 3.5)\n')
				f.write('project(%s-master  VERSION 1.0.0 LANGUAGES CXX)\n')
				f.write('include(ExternalProject)\n')
				self.write_master_for_project(project, f)

	def write_master_for_project(self, project, master_file):
		
		for dep_project in project.dependencies.values():
			self.write_master_for_project( dep_project, master_file)

		f = master_file
		f.write('\n')
		f.write('ExternalProject_Add(%s\n' % project.name)
		if len(project.dependencies) > 0:
			f.write('DEPENDS')
			for dep_project in project.dependencies.values():
				f.write(' %s' % dep_project.name)
		f.write('  SOURCE_DIR %s\n' % self.get_project_root_path(project))
		f.write('  CMAKE_ARGS -DCMAKE_INSTALL_PREFIX=${CMAKE_CURRENT_BINARY_DIR}/contrib/%s_install\n' % project.name)
		f.write('  INSTALL_DIR ${CMAKE_INSTALL_PREFIX}\n')
		f.write(')\n')
		
	def test_build(self, project):
		print('============= testing build of project %s' % project.name)
		build_root = '/tmp/%s.build' % project.name
		try:
			shutil.rmtree(build_root)
		except:
			pass
		os.mkdir(build_root)
		
		main_cmakelists_folder = self.get_project_root_path(project)
		if self.dep_handling_method == CMakeExporter.DepHandlingMethod.use_master:
			main_cmakelists_folder += '/cmake/master'
		
		call(["cmake", "-G", "Unix Makefiles", main_cmakelists_folder], cwd=build_root)
		call(["make"], cwd=build_root)
		
	def export_source_set(self, source_set):
		for project in source_set.projects.values():
			self.export_project(project)
		# test build
		for project in source_set.projects.values():
			self.test_build(project)
		



def create_example1_set():
	"""
	creates an example source set where the application game1 uses gameengine library, which requires some headers from math library
	
	:return SourceSet: the created SourceSet
	"""
	set1 = SourceSet()
	
	math_project = Project('mymath', ProjectType.static_library)
	math_project.add_source(SourceFile('vector.hpp', r"""#ifndef MATH_HPP
#define MATH_HPP
namespace math
{
	class Vector3
	{
	public:
		float m_elements[3];
	};
}
#endif //MATH_HPP
"""))

	set1.add_project(math_project)

	game_engine_project = Project('gameengine', ProjectType.static_library)
	game_engine_project.add_source(SourceFile('transform.hpp', r"""#ifndef TRANSFORM_HPP
#define TRANSFORM_HPP

#include <mymath/vector.hpp>

namespace gameengine
{
	class Transform
	{
	public:
		math::Vector3 getTranslation(void) const;
		
		float m_elements[4][4];
	};
}
#endif //TRANSFORM_HPP
"""))

	game_engine_project.add_source(SourceFile('transform.cpp', r"""#include <mymath/vector.hpp>
#include <gameengine/transform.hpp>

namespace gameengine
{
	math::Vector3 Transform::getTranslation(void) const
	{
		math::Vector3 translation;
		translation.m_elements[0] = m_elements[0][0];
		translation.m_elements[1] = m_elements[0][1];
		translation.m_elements[2] = m_elements[0][2];
		return translation;
	}	
}
"""))
	
	set1.add_project(game_engine_project)
	
	game_engine_project.add_dependency(math_project)
		
	#create_math_source(set_root_path+'/lib/libmath')
	#create_game_engine_source(set_root_path+'/lib/libgameengine')
	#create_game1_source()
	return set1
	
def test_dep_handling_methods():
	set1 = create_example1_set()
	for method in [ CMakeExporter.DepHandlingMethod.use_master, CMakeExporter.DepHandlingMethod.use_subdir ]:
		print("================ testing dependency handling method %s" % { CMakeExporter.DepHandlingMethod.use_master:'master', CMakeExporter.DepHandlingMethod.use_subdir:'subdir' }[method] )
		set_exporter = CMakeExporter('/tmp/example1', CMakeExporter.DepHandlingMethod.use_master)
		set_exporter.export_source_set(set1)

test_dep_handling_methods()